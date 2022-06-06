# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Inc. All rights reserved.
#
# This source code is licensed under the SHUUP® ENTERPRISE EDITION -
# END USER LICENSE AGREEMENT executed by Anders Innovations Inc. DBA as Shuup
# and the Licensee.
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from shuup_firebase_auth.views.auth import (
    FirebaseAuthView,
    FirebaseLogoutView,
    FirebaseResetPasswordView,
    get_auth_token,
)
from shuup_firebase_auth.views.customer_information import CustomerEditView

urlpatterns = [
    url(r"^auth/$", FirebaseAuthView.as_view(), name="auth"),
    url(r"^auth/reset-password/$", FirebaseResetPasswordView.as_view(), name="reset-password"),
    url(r"^auth-with-token/$", login_required(get_auth_token), name="auth-with-token"),
    url(r"^logout/$", FirebaseLogoutView.as_view(), name="logout"),
    url(r"^customer/$", CustomerEditView.as_view(), name="customer_edit"),
]

app_name = "shuup_firebase_auth"
