# -*- coding: utf-8 -*-
import logging, json
from django.contrib import auth
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.template import RequestContext
from django.template.loader import get_template
from django.apps import apps
from config import COBBLER_API_URL, INTERFACE_LANG, ZH_INTERFACE, EN_INTERFACE
from config import SSHOSTMGT_DB_SETTINGS
from opsweb.utils import login_required_json, login_permission_required, gen_dict, allNone

logger = logging.getLogger(__name__)

if INTERFACE_LANG == "en":
    INTERFACE = EN_INTERFACE
elif INTERFACE_LANG == "zh":
    INTERFACE = ZH_INTERFACE
else:
    INTERFACE = ZH_INTERFACE

apps.get_app_config("sshostmgt").db_settings = SSHOSTMGT_DB_SETTINGS
apps.get_app_config("sscobbler").settings = {
    "cobbler_api_url": COBBLER_API_URL,
    "interface_lang": INTERFACE_LANG,
    "zh_interface": ZH_INTERFACE,
    "en_interface": EN_INTERFACE
}

def custom404(request):
    response_obj = gen_response_obj(request, message = "Not Found.")
    return JsonResponse(response_obj, status = 404)

def gen_response_obj(request, message = None, collections = None, next = None):
    return {
        "message": message or "Method Not Allowed.",
        "collections": collections,
        "api_uri": request.get_raw_uri() if isinstance(request, HttpRequest) else None,
        "next": next
    }

@login_required_json
def index(request):
    response_obj = gen_response_obj(request)
    if request.method == "GET":
        t = get_template('sidebar.json.tmpl')
        # TODO: 设置用户信息
        # interface['username'] = username
        footer = {'version': "v1.0"}
        navbar = {'username': request.user.username}
        sidebar = t.render({'interface': INTERFACE})
        response_obj["message"] = "success."
        response_obj["collections"] = {
            "sidebar": json.loads(sidebar),
            "navbar": navbar,
            "footer": footer
        }
        return JsonResponse(response_obj, status = 200)
    else:
        return JsonResponse(response_obj, status = 405)

def login(request, username = None):
    response_obj = gen_response_obj(request)
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = auth.authenticate(username = username, password = password)
        if user is not None:
            auth.login(request, user)
            response_obj["message"] = "Login success."
            response_obj["collections"] = None
            return JsonResponse(response_obj, status = 200)
        else:
            response_obj["message"] = "Unauthorized."
            return JsonResponse(response_obj, status = 401)
    else:
        return JsonResponse(response_obj, status = 405)

def logout(request, username = None):
    response_obj = gen_response_obj(request)
    if request.method == "POST":
        auth.logout(request)
        response_obj["message"] = "Logout success."
        response_obj["next"] = request.build_absolute_uri(reverse("user_login"),
                                        kwargs = {"username": username})
        return JsonResponse(response_obj, status = 200)
    else:
        return JsonResponse(response_obj, status = 405)

@login_permission_required('user.add_user')
def create_user(request):
    response_obj = gen_response_obj(request)
    if request.method == "POST":
        post_dict = request.POST
        args = ("username", "password", "email", "first_name", "last_name")
        username = post_dict.get("username")
        email = post_dict.get("email")
        user_info = gen_dict(args, post_dict)
        logger.debug("Create a user: %s" % str(user_info))
        if not allNone(user_info):
            if User.objects.filter(username = username).exists() or \
               User.objects.filter(email = email).exists():
                response_obj["message"] = "Bad Request, user or email exists."
                return JsonResponse(response_obj, status = 400)
            user = User.objects.create_user(**user_info)
            user.save()
            response_obj["collections"][username] = {
                "username": username,
                "email": email
            }
            response_obj["message"] = "User created successful."
            return JsonResponse(response_obj, status = 201)
        else:
            response_obj["message"] = "Bad Request, Some Values Missed."
            return JsonResponse(response_obj, status = 400)
    else:
        return JsonResponse(response_obj, status = 405)

@login_permission_required('user.update_user')
def update_user(request):
    response_obj = gen_response_obj(request)
    if request.method == "POST":
        post_dict = request.POST
        args = ("username", "password", "email", "first_name", "last_name")
        username = post_dict.get("username")
        email = post_dict.get("email")
        user_info = gen_dict(args, post_dict)
        logger.debug("Update the user: %s" % str(user_info))
        if not allNone(user_info):
            user, created = User.objects.update_or_create(**user_info)
            user.save()
            response_obj["collections"][username] = {
                "username": username,
                "email": email
            }
            if created:
                response_obj["message"] = "User created successful."
            else:
                response_obj["message"] = "User updated successful."
            return JsonResponse(response_obj, status = 201)
        else:
            response_obj["message"] = "Bad Request, Some Values Missed."
            return JsonResponse(response_obj, status = 400)
    else:
        return JsonResponse(response_obj, status = 405)

@login_permission_required
def delete_user(request):
    pass

@login_permission_required
def change_user_perm(request):
    pass

@login_permission_required
def create_group(request):
    pass

@login_permission_required
def update_group(request):
    pass

@login_permission_required
def delete_group(request):
    pass

@login_permission_required
def change_group_perm(request):
    pass

@login_permission_required
def get_users(request):
    response_obj = gen_response_obj(request)
    if request.method == "GET":
        logger.debug("Request: %s" % dir(request))
        query_args = request.GET
        logger.info("Query Args: %s, %s, %s" % (str(query_args), type(query_args), dir(query_args)))
        filter_keys = ("email", "username", "name")
        filters = gen_dict(filter_keys, query_args)
        keys = ("order_by", "limiting", "which_page")
        users = get_users(filters, **gen_dict(keys, query_args))
        logger.info("User list: %s" % str(users))
        logger.debug("The type of users: %s" % type(users))
        if users:
            for item in users:
                response_obj["collections"][item.get("username")] = item
            response_obj["message"] = "success"
            return JsonResponse(response_obj, status = 200)
        else:
            response_obj["message"] = "Can't get any user."
            return JsonResponse(response_obj, status = 404)
    else:
        return JsonResponse(response_obj, status = 405)

@login_permission_required
def update_user(request, username = None):
    pass

@login_permission_required
def get_user(request, username = None):
    pass

@login_permission_required
def change_passwd(request, username = None):
    pass

@login_permission_required
def get_groups(request):
    pass

@login_permission_required
def update_group(request, groupname = None):
    pass

@login_permission_required
def get_group(request, groupname = None):
    pass
