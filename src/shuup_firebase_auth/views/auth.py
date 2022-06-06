# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Inc. All rights reserved.
#
# This source code is licensed under the SHUUP® ENTERPRISE EDITION -
# END USER LICENSE AGREEMENT executed by Anders Innovations Inc. DBA as Shuup
# and the Licensee.
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME, get_user_model, login, logout
from django.http.response import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, TemplateView
from firebase_admin import auth as firebase_auth
from registration.backends.simple import views as simple_views
from registration.signals import user_registered
from shuup.admin.supplier_provider import get_supplier
from shuup.core.models import get_person_contact
from shuup.front.apps.registration.views import RegistrationViewMixin
from shuup.front.utils.user import is_admin_user

from shuup_firebase_auth.forms import FireBaseAuthAndRegisterForm, ResetPasswordForm
from shuup_firebase_auth.models import FirebaseUser
from shuup_firebase_auth.signals import user_registered as firebase_user_registered
from shuup_firebase_auth.utils import get_firebase_app


class FirebaseAuthView(RegistrationViewMixin, simple_views.RegistrationView):
    template_name = "shuup_firebase_auth/auth.jinja"
    form_class = FireBaseAuthAndRegisterForm

    @method_decorator(sensitive_post_parameters("password1", "password2"))
    def dispatch(self, request, *args, **kwargs):
        if is_admin_user(request):
            return super(FormView, self).dispatch(request, *args, **kwargs)
        return super(FirebaseAuthView, self).dispatch(request, *args, **kwargs)
    
    def form_invalid(self, form):
        errors = list(form.non_field_errors())
        for error in errors:
            messages.error(self.request, error)
        return HttpResponseRedirect(reverse("shuup_firebase_auth:auth"))

    def get_success_url(self, *args, **kwargs):
        if is_admin_user(self.request) or get_supplier(self.request):
            return reverse("shuup_admin:dashboard")

        url = self.request.POST.get(REDIRECT_FIELD_NAME)
        if url and is_safe_url(url, self.request.get_host()):
            return url
        return reverse("shuup:dashboard")

    def register(self, form):
        user, registered = form.save()
        if not user or not registered:
            return HttpResponseRedirect(reverse("shuup_firebase_auth:auth"))
        if registered:
            get_person_contact(user).add_to_shop(self.request.shop)
            auth_user = get_user_model().objects.get(pk=user.pk)
            auth_user.backend = "django.contrib.auth.backends.ModelBackend"
            login(self.request, auth_user)
            user_registered.send(sender=self.__class__, user=auth_user, request=self.request)
            firebase_user_registered.send(sender=self.__class__, user=auth_user, request=self.request)
        else:
            auth_user = get_user_model().objects.get(pk=user.pk)
            auth_user.backend = "django.contrib.auth.backends.ModelBackend"
            login(self.request, auth_user)
        return auth_user


class FirebaseLogoutView(TemplateView):
    template_name = "shuup_firebase_auth/logout.jinja"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
        return super(FirebaseLogoutView, self).dispatch(request, *args, **kwargs)


class FirebaseResetPasswordView(TemplateView):
    template_name = "shuup_firebase_auth/reset_password.jinja"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = ResetPasswordForm()
        return context


def get_auth_token(request):
    if request.user.is_authenticated:
        firebase_user = FirebaseUser.objects.filter(user=request.user).first()
        if firebase_user:
            app = get_firebase_app()
            token = firebase_auth.create_custom_token(firebase_user.uid, app=app)
            return JsonResponse({"token": token.decode("utf-8")}, status=200)
    return JsonResponse({"error": "not authenticated"}, status=400)
