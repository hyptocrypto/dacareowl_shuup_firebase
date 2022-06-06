# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Inc. All rights reserved.
#
# This source code is licensed under the SHUUP® ENTERPRISE EDITION -
# END USER LICENSE AGREEMENT executed by Anders Innovations Inc. DBA as Shuup
# and the Licensee.
import django_jinja
import jinja2
from django.conf import settings


@django_jinja.library.global_function
@jinja2.contextfunction
def get_firebase_settings(context):
    return {
        "apiKey": settings.SHUUP_FIREBASE_AUTH_SETTINGS["API_KEY"],
        "authDomain": settings.SHUUP_FIREBASE_AUTH_SETTINGS["AUTH_DOMAIN"],
        "databaseURL": settings.SHUUP_FIREBASE_AUTH_SETTINGS.get("DATABASE_URL", ""),
        "projectId": settings.SHUUP_FIREBASE_AUTH_SETTINGS["PROJECT_ID"],
        "storageBucket": settings.SHUUP_FIREBASE_AUTH_SETTINGS["STORAGE_BUCKET"],
        "messagingSenderId": settings.SHUUP_FIREBASE_AUTH_SETTINGS["MESSAGING_SENDER_ID"],
        "appId": settings.SHUUP_FIREBASE_AUTH_SETTINGS["APP_ID"],
    }


@django_jinja.library.global_function
def get_firebase_auth_providers():
    return settings.SHUUP_FIREBASE_AUTH_PROVIDERS


@django_jinja.library.global_function
def get_firebase_auth_provider_args():
    return settings.SHUUP_FIREBASE_AUTH_PROVIDER_ARGS
