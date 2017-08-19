# -*- coding: utf-8 -*-
from django.http.request import QueryDict

def merge_dicts(*args):
    if len(args) == 0:
        return args
    elif len(args) == 1:
        return args[0]
    else:
        return dict(args[0], **merge_dicts(*args[1:]))

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
