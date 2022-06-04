# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Inc. All rights reserved.
#
# This source code is licensed under the SHUUP® ENTERPRISE EDITION -
# END USER LICENSE AGREEMENT executed by Anders Innovations Inc. DBA as Shuup
# and the Licensee.

import logging

from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.transaction import atomic
from django.utils.translation import gettext_lazy as _
from firebase_admin import auth as firebase_auth
from shuup.core.models import get_person_contact, Contact
from shuup.front.signals import person_registration_save

from shuup_firebase_auth.models import FirebaseUser
from shuup_firebase_auth.utils import get_firebase_app

LOGGER = logging.getLogger(__name__)


class BaseFirebaseRegistrationForm(forms.Form):
    id_token = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

    def clean(self):
        data = super().clean()
        app = get_firebase_app()
        
        try:
            token_data = firebase_auth.verify_id_token(data["id_token"], app=app)
        except Exception:
            LOGGER.exception("Failed to validate user token")
            raise forms.ValidationError(_("Invalid user token."))

        if not token_data.get("email"):
            raise forms.ValidationError(_("Missing email address."))

        firebase_user = firebase_auth.get_user_by_email(token_data["email"])

        #NOTE This is a check to prevent a user from accidentialy creating a parent/contact when trying to login as a daycare.
        # User Story Issue: User registers as a daycare, is waiting for approval, goes to singin via the logical singin button leading to /auth.
        # They then input the email and password used when regsitering the daycare, this leads to firebase creating a user account for them.
        # They will then recive the email verification email, after verify the email, a parent account is created in the shuup end. This leads to login issues.
        if Contact.objects.filter(email=token_data.get("email")).exists():
            firebase_auth.delete_user(firebase_user.uid)
            messages.add_message(self.request, messages.WARNING, _("It looks like you are trying to create an account with an exisiting account. Please make sure you are using the correct login method."))
            return HttpResponseRedirect(reverse("shuup_firebase_auth:auth"))

        data.update(
            {
                "uid": token_data["uid"],
                "name": firebase_user.display_name,
                "email": token_data["email"],
                "phone": firebase_user.phone_number,
            }
        )
        return data


class FireBaseAuthAndRegisterForm(BaseFirebaseRegistrationForm):
    def clean(self):
        data = super().clean()
        if not data.get("uid"):
            return data
        
        firebase_user = FirebaseUser.objects.filter(uid=data["uid"]).first()
        if firebase_user:  # No need to clean more
            return data

        try:
            existing_user = get_user_model().objects.get(username=data["email"])
            FirebaseUser.objects.update_or_create(user=existing_user, defaults=dict(uid=data["uid"]))
        except get_user_model().DoesNotExist:
            pass

        return data

    def save(self, *args, **kwargs):
        with atomic():
            data = self.cleaned_data
            if not data.get("uid"):
                return None, False
            # existing user
            firebase_user = FirebaseUser.objects.filter(uid=data["uid"]).first()
            if firebase_user:
                contact = get_person_contact(firebase_user.user)
                contact.name = data["name"] or ""
                contact.phone = data["phone"] or ""
                contact.save()
                return firebase_user.user, False

            user = get_user_model().objects.create(username=data["email"], email=data["email"])
            user.set_unusable_password()
            contact = get_person_contact(user)
            contact.name = data["name"] or ""
            contact.email = data["email"]
            contact.phone = data["phone"] or ""
            contact.save()
            contact.add_to_shop(self.request.shop)
            FirebaseUser.objects.update_or_create(user=user, defaults=dict(uid=data["uid"]))
            person_registration_save.send(sender=type(self), request=self.request, user=user, contact=contact)
            return user, True


class FirebaseLoginForm(BaseFirebaseRegistrationForm):
    def clean(self):
        data = super().clean()

        firebase_user = FirebaseUser.objects.filter(uid=data["uid"]).first()
        if not firebase_user:
            raise forms.ValidationError(_("User not found. Please register first."))

        data["user"] = firebase_user.user
        return data

    def get_user(self):
        return self.cleaned_data["user"]


class ResetPasswordForm(forms.Form):
    email = forms.EmailField(label=_("Account email"))
