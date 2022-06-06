# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Inc. All rights reserved.
#
# This source code is licensed under the SHUUP® ENTERPRISE EDITION -
# END USER LICENSE AGREEMENT executed by Anders Innovations Inc. DBA as Shuup
# and the Licensee.
from django.conf import settings
from django.urls import reverse
from shuup.core.utils.static import get_shuup_static_url
from shuup.xtheme.resources import InlineScriptResource, add_resource

ADD_FIREBASE_CONFIG = """
    window.FirebaseAuthConfig = %(data)s;
"""

ADD_AUTO_LOGIN = """
if (window.firebase) {
    firebase.auth().useDeviceLanguage();
    firebase.auth().onAuthStateChanged(function(user) {
        if (user) {
            window.authenticateWithToken('%(email)s', '%(url)s');
        }
    });
}
"""

ADD_AUTO_LOGOUT = """
if (window.firebase) {
    firebase.auth().signOut();
}
"""


def add_resources(context, content):
    if not context.get("view"):
        return

    request = context.get("request")
    add_resource(context, "head_end", get_shuup_static_url("shuup-firebase-auth.css", "shuup-firebase-auth"))
    add_resource(
        context,
        "head_end",
        InlineScriptResource(
            ADD_FIREBASE_CONFIG
            % {
                "data": {
                    "apiKey": settings.SHUUP_FIREBASE_AUTH_SETTINGS["API_KEY"],
                    "authDomain": settings.SHUUP_FIREBASE_AUTH_SETTINGS["AUTH_DOMAIN"],
                    "databaseURL": settings.SHUUP_FIREBASE_AUTH_SETTINGS.get("DATABASE_URL", ""),
                    "projectId": settings.SHUUP_FIREBASE_AUTH_SETTINGS["PROJECT_ID"],
                    "storageBucket": settings.SHUUP_FIREBASE_AUTH_SETTINGS["STORAGE_BUCKET"],
                    "messagingSenderId": settings.SHUUP_FIREBASE_AUTH_SETTINGS["MESSAGING_SENDER_ID"],
                    "appId": settings.SHUUP_FIREBASE_AUTH_SETTINGS["APP_ID"],
                }
            }
        ),
    )
    add_resource(context, "head_end", get_shuup_static_url("shuup-firebase-auth.js", "shuup-firebase-auth"))

    if request.user.is_authenticated:
        add_resource(
            context,
            "body_end",
            InlineScriptResource(
                ADD_AUTO_LOGIN % {"email": request.user.email, "url": reverse("shuup_firebase_auth:auth-with-token")}
            ),
        )
    else:
        if request.path != reverse("shuup_firebase_auth:auth"):
            add_resource(context, "head_end", InlineScriptResource(ADD_AUTO_LOGOUT))
