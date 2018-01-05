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
        # 管理员
        if request.user.is_staff:
            return True
        if hasattr(obj, 'get_username'):
            # request.user实际上是user实例
            return request.user.get_username() == obj.get_username()
        elif hasattr(obj, 'owner'):
            return request.user == obj.owner
        elif hasattr(obj, 'owners'):
            return request.user in obj.owners.all()
        elif hasattr(obj, 'user'):
            return request.user == obj.user
        elif hasattr(obj, 'users'):
            return request.user in obj.users.all()

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow admin to edit it.
    """

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'get_username'):
            # request.user实际上是user实例
            return request.user.get_username() == obj.get_username()
        elif hasattr(obj, 'owner'):
            return request.user == obj.owner
        elif hasattr(obj, 'owners'):
            return request.user in obj.owners.all()
        elif hasattr(obj, 'user'):
            return request.user == obj.user
        elif hasattr(obj, 'users'):
            return request.user in obj.users.all()

class CustomDjangoModelPermissions(permissions.BasePermission):
    """
    The request is authenticated using `django.contrib.auth` permissions.
    See: https://docs.djangoproject.com/en/dev/topics/auth/#permissions
    It ensures that the user is authenticated, and has the appropriate
    `add`/`change`/`delete` permissions on the model.
    This permission can only be applied against view classes that
    provide a `.queryset` attribute.
    """

    # Map methods into required permission codes.
    # Override this if you need to also provide 'view' permissions,
    # or if you want to provide custom permission codes.
    perms_map = {
        'GET': ['%(app_label)s.list_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    authenticated_users_only = True

    def get_required_permissions(self, method, model_cls):
        """
        Given a model and an HTTP method, return the list of permission
        codes that the user is required to have.
        """
        kwargs = {
            'app_label': model_cls._meta.app_label,
            'model_name': model_cls._meta.model_name
        }

        if method not in self.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return [perm % kwargs for perm in self.perms_map[method]]

    def _queryset(self, view):
        assert hasattr(view, 'get_queryset') \
            or getattr(view, 'queryset', None) is not None, (
            'Cannot apply {} on a view that does not set '
            '`.queryset` or have a `.get_queryset()` method.'
        ).format(self.__class__.__name__)

        if hasattr(view, 'get_queryset'):
            queryset = view.get_queryset()
            assert queryset is not None, (
                '{}.get_queryset() returned None'.format(view.__class__.__name__)
            )
            return queryset
        return view.queryset

    def has_permission(self, request, view):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        if not request.user or (
           not request.user.is_authenticated and self.authenticated_users_only):
            return False

        queryset = self._queryset(view)
        # 访问此model需要的权限
        perms = self.get_required_permissions(request.method, queryset.model)
        all_group_perms = list(request.user.get_group_permissions())
        # OPTIONS/HEAD no perms
        # Each method in perms_map only have one perm, so can use len(perms) == 1.
        if len(perms) == 1:
            if perms[0] in all_group_perms:
                perm_flag = True
            else:
                perm_flag = False

        return request.user.has_perms(perms) or perm_flag
