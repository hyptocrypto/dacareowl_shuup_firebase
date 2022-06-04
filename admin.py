# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Inc. All rights reserved.
#
# This source code is licensed under the SHUUP® ENTERPRISE EDITION -
# END USER LICENSE AGREEMENT executed by Anders Innovations Inc. DBA as Shuup
# and the Licensee.
from django.utils.translation import ugettext_lazy as _
from shuup.admin.base import AdminModule, MenuEntry
from shuup.admin.utils.urls import admin_url


class MyProfileModule(AdminModule):
    name = _("My Profile")
    breadcrumbs_menu_entry = MenuEntry(name, url="shuup_admin:firebase_my_profile")

    def get_urls(self):
        return [
            admin_url(
                r"^profile/$",
                "shuup_firebase_auth.views.customer_information.CustomerAdminEditView",
                name="firebase_my_profile",
            )
        ]

    def get_menu_entries(self, request):
        return [
            MenuEntry(
                text=self.name,
                icon="fa fa-list",
                url="shuup_admin:firebase_my_profile",
                category=self.name,
                ordering=9999,
            )
        ]
