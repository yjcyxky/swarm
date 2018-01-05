# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import requests
import json
import os
import logging
import time
from urllib.parse import urlparse
from django.apps import apps
from rest_framework import status
from ssfalcon.utils import url_path_join

logger = logging.getLogger(__name__)

ssfalcon_settings = apps.get_app_config('ssfalcon').settings
SSFALCON_API_PREFIX = ssfalcon_settings.get('falcon_api_prefix', 'http://127.0.0.1/api/v1/')
USERNAME = ssfalcon_settings.get('name', 'admin')
PASSWORD = ssfalcon_settings.get('password', 'admin@nordata.cn')
TIMEOUT = ssfalcon_settings.get('TIMEOUT', 10)
login_date = None

def get_token(name, password):
    form_data = {'name': name, 'password': password}
    url = url_path_join(SSFALCON_API_PREFIX, '/user/login')
    login = requests.post(url, json = form_data)
    if login.status_code == 200:
        json_obj = login.json()
        token = json_obj.get('sig')
        login_name = json_obj.get('name')
        admin = json_obj.get('admin')
        api_token = '{"name": "%s","sig":"%s"}' % (login_name, token)
        headers = {
            'Apitoken': api_token,
            'Content-Type': 'application/json'
        }
        logger.debug("Log in with %s-%s" % (login_name, admin))
        logger.debug("Headers: %s" % headers)
        login_date = int(time.time())
        return headers
    else:
        logger.error(login.json())
        logger.error("Status Code: %s" % login.status_code)
        logger.error("Get Token Error.")
        return False

def check_expired_token(json_obj):
    if isinstance(json_obj, dict):
        if not json_obj.get("error") and json_obj.get("error") == "not found this user":
            return get_token(USERNAME, PASSWORD)
    return False

def get_data(endpoint, json_data = None, form_data = None, method = 'GET',
             headers = None, params = None, timeout = TIMEOUT):
    now = int(time.time())
    if login_date is None or now >= login_date + timeout:
        headers = get_token(USERNAME, PASSWORD)
    url = url_path_join(SSFALCON_API_PREFIX, endpoint)
    func_dicts = {
        'GET': requests.get,
        'POST': requests.post,
        'PUT': requests.put,
        'DELETE': requests.delete
    }
    if method not in ('GET', 'POST', 'PUT', 'DELETE'):
        logger.error("No such method: %s" % method)
    else:
        func = func_dicts.get(method)
        logger.debug("%s-%s-%s" % (url, str(headers), str(form_data)))
        data = func(url, headers = headers, json = json_data, data = form_data)
        status_code = data.status_code
        if status_code == status.HTTP_200_OK:
            json_obj = data.json()
        else:
            json_obj = data.text
        logger.debug("JSON Data: %s" % json_obj)
        headers = check_expired_token(json_obj)
        if headers:
            data = func(url,  params = params, headers = headers, data = form_data,
                        json = json_data)
            status_code = data.status_code
        if status_code == status.HTTP_200_OK:
            json_obj = data.json()
        else:
            json_obj = data.text
        return status_code, json_obj
