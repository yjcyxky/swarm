# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class SsfalconConfig(AppConfig):
    name = "ssfalcon"
    settings = {
        "falcon_api_prefix": "http://192.168.1.116:8080/api/v1/",
        "name": "test",
        "password": "test"
    }
