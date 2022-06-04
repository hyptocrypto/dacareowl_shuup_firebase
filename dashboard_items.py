# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Inc. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from django.utils.translation import ugettext_lazy as _
from shuup.front.utils.dashboard import DashboardItem


class CustomerDashboardItem(DashboardItem):
    template_name = "shuup_firebase_auth/customer_dashboard_item.jinja"
    title = _("Customer Information")
    icon = "fa fa-user"
    _url = "shuup_firebase_auth:customer_edit"

    def get_context(self):
        context = super(CustomerDashboardItem, self).get_context()
        customer = self.request.customer
        context["customer"] = customer
        return context
