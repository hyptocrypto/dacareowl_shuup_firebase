# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Inc. All rights reserved.
#
# This source code is licensed under the SHUUP® ENTERPRISE EDITION -
# END USER LICENSE AGREEMENT executed by Anders Innovations Inc. DBA as Shuup
# and the Licensee.
import firebase_admin
from django.conf import settings

_FIREBASE_APP = None


def get_firebase_app():
    global _FIREBASE_APP
    if _FIREBASE_APP is None:
        cert = getattr(settings, "SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_FILE", None) or getattr(
            settings, "SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_DICT", None
        )
        credentials = firebase_admin.credentials.Certificate(cert)
        _FIREBASE_APP = firebase_admin.initialize_app(credentials)
    return _FIREBASE_APP
