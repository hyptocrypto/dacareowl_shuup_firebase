# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Inc. All rights reserved.
#
# This source code is licensed under the SHUUP® ENTERPRISE EDITION -
# END USER LICENSE AGREEMENT executed by Anders Innovations Inc. DBA as Shuup
# and the Licensee.
from django import forms
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.timezone import get_current_timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView
from firebase_admin import auth as firebase_auth
from shuup.core.models import MutableAddress, PersonContact, get_company_contact, get_person_contact
from shuup.core.utils.forms import MutableAddressForm
from shuup.front.forms.widget import PictureDnDUploaderWidget
from shuup.front.views.dashboard import DashboardViewMixin
from shuup.utils.form_group import FormGroup
from shuup.utils.importing import cached_load

from shuup_firebase_auth.models import FirebaseUser
from shuup_firebase_auth.utils import get_firebase_app


class AddressForm(MutableAddressForm):
    class Meta:
        model = MutableAddress
        fields = (
            "name",
            "name_ext",
            "phone",
            "email",
            "street",
            "street2",
            "postal_code",
            "city",
            "region",
            "region_code",
            "country",
        )
        labels = {"postal_code": _("Zip code"), "region_code": _("State")}

    def __init__(self, **kwargs):
        super(AddressForm, self).__init__(**kwargs)
        if not kwargs.get("instance"):
            # Set default country
            self.fields["country"].initial = settings.SHUUP_ADDRESS_HOME_COUNTRY

        for field_key in self.fields:
            self.fields[field_key].required = False


class PersonContactForm(forms.ModelForm):
    class Meta:
        model = PersonContact
        fields = ("first_name", "last_name", "phone", "email", "timezone", "marketing_permission", "picture")

    def __init__(self, *args, **kwargs):
        super(PersonContactForm, self).__init__(*args, **kwargs)
        for field in ("first_name", "last_name"):
            self.fields[field].required = True

        self.fields["email"].widget.attrs["readonly"] = True
        self.initial["timezone"] = get_current_timezone()

        if settings.SHUUP_CUSTOMER_INFORMATION_ALLOW_PICTURE_UPLOAD:
            self.fields["picture"].widget = PictureDnDUploaderWidget(clearable=True)
        else:
            self.fields.pop("picture")

        field_properties = settings.SHUUP_PERSON_CONTACT_FIELD_PROPERTIES
        for field, properties in field_properties.items():
            for prop in properties:
                setattr(self.fields[field], prop, properties[prop])

    def save(self, commit=True):
        return super(PersonContactForm, self).save(commit)


class CustomerInformationFormGroup(FormGroup):
    address_forms = settings.SHUUP_FIREBASE_AUTH_ADDRESS_KINDS

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(CustomerInformationFormGroup, self).__init__(*args, **kwargs)
        contact = get_person_contact(self.request.user)
        address_form_class = cached_load("SHUUP_FIREBASE_AUTH_ADDRESS_FORM")
        for form_name in self.address_forms:
            self.add_form_def(
                form_name, address_form_class, kwargs={"instance": getattr(contact, "default_%s_address" % form_name)}
            )

        person_contact_form_class = cached_load("SHUUP_FIREBASE_AUTH_PERSON_CONTACT_FORM")
        self.add_form_def("contact", person_contact_form_class, kwargs={"instance": contact})

    def save(self):
        contact = self.forms["contact"].save()
        user = contact.user

        if "billing" in self.forms:
            billing_address = self.forms["billing"].save()
            if billing_address.pk != contact.default_billing_address_id:  # Identity changed due to immutability
                contact.default_billing_address = billing_address

        if "shipping" in self.forms:
            shipping_address = self.forms["shipping"].save()
            if shipping_address.pk != contact.default_shipping_address_id:  # Identity changed due to immutability
                contact.default_shipping_address = shipping_address

        if not bool(get_company_contact(self.request.user)):  # Only update user details for non-company members
            user.email = contact.email
            user.first_name = contact.first_name
            user.last_name = contact.last_name
            user.save()

        firebase_user = FirebaseUser.objects.filter(user=user).first()
        if firebase_user:
            get_firebase_app()
            firebase_auth.update_user(firebase_user.uid, display_name=contact.name)

        contact.save()
        return contact


class CustomerEditView(DashboardViewMixin, FormView):
    template_name = "shuup_firebase_auth/edit_customer.jinja"

    def get_form_class(self):
        return CustomerInformationFormGroup

    def get_form_kwargs(self):
        kwargs = super(CustomerEditView, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _("Account information saved successfully."))
        return redirect("shuup_firebase_auth:customer_edit")


class CustomerAdminEditView(FormView):
    template_name = "shuup_firebase_auth/edit_admin_customer.jinja"

    def get_form_class(self):
        return CustomerInformationFormGroup

    def get_form_kwargs(self):
        kwargs = super(CustomerAdminEditView, self).get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _("Account information saved successfully."))
        return redirect("shuup_admin:firebase_my_profile")
