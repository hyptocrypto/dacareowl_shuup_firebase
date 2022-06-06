# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Inc. All rights reserved.
#
# This source code is licensed under the SHUUP® ENTERPRISE EDITION -
# END USER LICENSE AGREEMENT executed by Anders Innovations Inc. DBA as Shuup
# and the Licensee.
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME, get_user_model, login
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import is_safe_url
from registration.backends.simple import views as simple_views
from registration.signals import user_registered
from shuup.core.models import get_person_contact
from shuup.front.apps.registration.views import RegistrationViewMixin

from shuup_firebase_auth.forms import FireBaseAuthAndRegisterForm
from shuup_firebase_auth.signals import user_registered as firebase_user_registered


class FirebaseRegisterView(RegistrationViewMixin, simple_views.RegistrationView):
    SEND_ACTIVATION_EMAIL = settings.SHUUP_REGISTRATION_REQUIRES_ACTIVATION
    form_class = FireBaseAuthAndRegisterForm

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse("shuup:registration_register"))

    def form_invalid(self, form):
        errors = list(form.non_field_errors())
        for error in errors:
            messages.error(self.request, error)
        return HttpResponseRedirect(reverse("shuup:registration_register"))

    def get_success_url(self, *args, **kwargs):
        if settings.SHUUP_FIREBASE_AUTH_REGISTER_FINISH_URL:
            return reverse(settings.SHUUP_FIREBASE_AUTH_REGISTER_FINISH_URL)

        url = self.request.POST.get(REDIRECT_FIELD_NAME)
        if url and is_safe_url(url, self.request.get_host()):
            return url

        return reverse("shuup:registration_complete")

    def register(self, form):
        user, _ = form.save()
        get_person_contact(user).add_to_shop(self.request.shop)

        auth_user = get_user_model().objects.get(pk=user.pk)
        auth_user.backend = "django.contrib.auth.backends.ModelBackend"
        login(self.request, auth_user)
        user_registered.send(sender=self.__class__, user=auth_user, request=self.request)
        firebase_user_registered.send(sender=self.__class__, user=auth_user, request=self.request)
        return auth_user
