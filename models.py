# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2021, Shuup Inc. All rights reserved.
#
# This source code is licensed under the SHUUP® ENTERPRISE EDITION -
# END USER LICENSE AGREEMENT executed by Anders Innovations Inc. DBA as Shuup
# and the Licensee.
from django.conf import settings
from django.db import models


class FirebaseUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="firebase_user", on_delete=models.CASCADE)
    uid = models.CharField(max_length=255, unique=True)
