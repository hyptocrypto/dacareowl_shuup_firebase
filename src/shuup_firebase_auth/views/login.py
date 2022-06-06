# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Inc. All rights reserved.
#
# This source code is licensed under the SHUUP® ENTERPRISE EDITION -
# END USER LICENSE AGREEMENT executed by Anders Innovations Inc. DBA as Shuup
# and the Licensee.
from django.contrib import messages
from django.contrib.auth import login
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from shuup.front.apps.auth.views import LoginView

from shuup_firebase_auth.forms import FirebaseLoginForm
from shuup_firebase_auth.signals import user_authenticated


class FirebaseLoginView(LoginView):
    form_class = FirebaseLoginForm

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse("shuup:login"))

    def form_invalid(self, form):
        errors = list(form.non_field_errors())
        for error in errors:
            messages.error(self.request, error)
        return HttpResponseRedirect(reverse("shuup:login"))

    def form_valid(self, form):
        user = form.get_user()
        if user:
            user.backend = "django.contrib.auth.backends.ModelBackend"
            login(self.request, user)
            user_authenticated.send(sender=self.__class__, user=user, request=self.request)

        return HttpResponseRedirect(self.get_success_url())
