# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow admin to edit it.
    """

    def has_object_permission(self, request, view, obj):
        try:
            # 管理员
            if request.user.is_staff:
                return True
            if obj.get_username():
                # request.user实际上是user实例
                return request.user.get_username() == obj.get_username()
            else:
                return request.user == obj.owner
        except AttributeError:
            pass
