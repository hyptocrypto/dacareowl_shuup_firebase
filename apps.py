# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Inc. All rights reserved.
#
# This source code is licensed under the SHUUP® ENTERPRISE EDITION -
# END USER LICENSE AGREEMENT executed by Anders Innovations Inc. DBA as Shuup
# and the Licensee.
import shuup.apps


class AppConfig(shuup.apps.AppConfig):
    name = "shuup_firebase_auth"
    label = "shuup_firebase_auth"
    provides = {
        "front_urls_pre": ["shuup_firebase_auth.urls:urlpatterns"],
    }
