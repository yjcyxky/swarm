# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
import platform

class SscobwebConfig(AppConfig):
    name = "sscobweb"
    settings = {
        'ROOT_PREFIX': '/opt/local/cobweb',
        'SYSTEM': 'Linux',
        'ARCH': 'x86_64'
    }
