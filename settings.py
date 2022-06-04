# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Inc. All rights reserved.
#
# This source code is licensed under the SHUUP® ENTERPRISE EDITION -
# END USER LICENSE AGREEMENT executed by Anders Innovations Inc. DBA as Shuup
# and the Licensee.

#: The base registration model
SHUUP_FIREBASE_AUTH_BASE_REGISTER_FORM = "shuup_firebase_auth.forms.registration.FirebaseBaseRegistrationForm"

#: Firebase Authentication settings
#: Get these from your project settings
SHUUP_FIREBASE_AUTH_SETTINGS = {
    "API_KEY": "",
    "AUTH_DOMAIN": "",
    "DATABASE_URL": "",
    "PROJECT_ID": "",
    "STORAGE_BUCKET": "",
    "MESSAGING_SENDER_ID": "",
    "APP_ID": "",
}

#: The path to the Admin SDK Private Key
#: Generate it at https://console.firebase.google.com/project/_/settings/serviceaccounts/adminsdk
SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_FILE = None

#: The Admin SDK Private content as a dictionary
SHUUP_FIREBASE_AUTH_ACCOUNT_KEY_DICT = None

#: The URL to redirect the user to finish the registration, when needed
SHUUP_FIREBASE_AUTH_REGISTER_FINISH_URL = ""

#: The enabled sign-in providers
SHUUP_FIREBASE_AUTH_PROVIDERS = ["email", "google", "facebook", "apple"]

#: Extra arguments to pass to the authentication providers.
#: See options from: https://github.com/firebase/firebaseui-web#generic-oauth-provider
#: Passing a value with the ``"provider"`` key does nothing since the providers themselves
#: come from the ``SHUUP_FIREBASE_AUTH_PROVIDERS`` setting.
#: Example usage to change all button text from 'Sign in ...' to 'Sign up ...':
#:
#: SHUUP_FIREBASE_AUTH_PROVIDER_ARGS = {
#:     "email": {
#:         "fullLabel": "Sign up with email",
#:     },
#:     "google": {
#:         "fullLabel": "Sign up with Google",
#:     },
#:     "facebook": {
#:         "fullLabel": "Sign up with Facebook",
#:     },
#: }
#:
SHUUP_FIREBASE_AUTH_PROVIDER_ARGS = {}

#: Which address options to show in contact information page
SHUUP_FIREBASE_AUTH_ADDRESS_KINDS = ["billing", "shipping"]

#: Which address form to show in contact information page
SHUUP_FIREBASE_AUTH_ADDRESS_FORM = "shuup_firebase_auth.views.customer_information.AddressForm"

#: Which person contact form to show in contact information page
SHUUP_FIREBASE_AUTH_PERSON_CONTACT_FORM = "shuup_firebase_auth.views.customer_information.PersonContactForm"
