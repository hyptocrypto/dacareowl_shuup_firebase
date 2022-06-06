# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Inc. All rights reserved.
#
# This source code is licensed under the SHUUP® ENTERPRISE EDITION -
# END USER LICENSE AGREEMENT executed by Anders Innovations Inc. DBA as Shuup
# and the Licensee.
from django.conf.urls import url

from shuup_firebase_auth.views.login import FirebaseLoginView
from shuup_firebase_auth.views.register import FirebaseRegisterView

urlpatterns = [
    url(r"^social-auth/register/$", FirebaseRegisterView.as_view(), name="firebase-auth.register"),
    url(r"^social-auth/login/$", FirebaseLoginView.as_view(), name="firebase-auth.login"),
]

app_name = "shuup_firebase_auth"
