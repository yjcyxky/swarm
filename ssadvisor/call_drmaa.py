import logging
import re
import requests
import hashlib
import os
import json
import uuid
import time
from rest_framework import status
from django.db.models import Q
from django.db import transaction
from ssadvisor.exceptions import (AdvisorWrongSetting)
from ssadvisor.models import Setting

logger = logging.getLogger(__name__)

def get_settings():
    try:
        settings = Setting.objects.filter(is_active = 1)
        current_setting = settings[0]
        return current_setting
    except Setting.DoesNotExist:
        raise AdvisorWrongSetting('No Advisor Setting.')

class Report:
    pass


class Task:
    pass
