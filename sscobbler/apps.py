# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class SscobblerConfig(AppConfig):
    name = "sscobbler"
    settings = {
        "cobbler_api_url": "",
        "interface_lang": "en",
        "zh_interface": None,
        "en_interface": None
    }
