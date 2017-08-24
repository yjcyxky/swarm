# -*- coding: utf-8 -*-
from functools import wraps
from django.shortcuts import reverse
from django.core.exceptions import PermissionDenied

def test_user_passes(test_func):
    """
    Decorator for views that checks that the user passes the given test
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            response_obj = {
                "message": "Method Not Allowed.",
                "collections": None,
                "api_uri": request.get_raw_uri(),
            }
            from django.http import JsonResponse
            if request.method == "POST":
                username = request.POST.get("username")
                if username is None or username == '':
                    response_obj["message"] = "Bad Request, Some Values Missed."
                    return JsonResponse(response_obj, status = 400)
                response_obj["message"] = "Not Allowed to Access."
                response_obj["next"] = request.build_absolute_uri(reverse("user_login",
                                                kwargs = {"username": username}))
                return JsonResponse(response_obj, status = 401)
            else:
                return JsonResponse(response_obj, status = 405)
        return _wrapped_view
    return decorator

def login_required(function = None):
    """
    Decorator for views that checks that the user is logged in.
    """
    actual_decorator = test_user_passes(lambda u: u.is_authenticated)
    if function:
        return actual_decorator(function)
    return actual_decorator

def login_permission_required(perm, raise_exception=False):
    """
    Decorator for views that checks whether a user has a particular permission
    enabled, redirecting to the log-in page if necessary.
    If the raise_exception parameter is given the PermissionDenied exception
    is raised.
    """
    def check_perms(user):
        if isinstance(perm, str):
            perms = (perm, )
        else:
            perms = perm
        # check if the user login.
        if user.is_authenticated:
            # First check if the user has the permission (even anon users)
            if user.has_perms(perms):
                return True
            # In case the 403 handler should be called raise the exception
            if raise_exception:
                raise PermissionDenied
        # As the last resort, show the login form
        return False
    return test_user_passes(check_perms)

def gen_dict(keys, src_obj):
    desc_obj = {}
    if isinstance(src_obj, dict):
        for key in keys:
            desc_obj[key] = src_obj.get(key)
    elif isinstance(src_obj, QueryDict):
        for key in keys:
            desc_obj[key] = src_obj.get(key)
    return desc_obj

def isNone(obj):
    if obj is None:
        return True
    else:
        return False

def allNone(objs):
    if isinstance(objs, (list, tuple)):
        for item in objs:
            if not isNone(item):
                return False
            else:
                continue
        return True
