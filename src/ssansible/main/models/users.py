# pylint: disable=protected-access,no-member
from __future__ import unicode_literals

import logging

from django.contrib.auth.models import Group as BaseGroup
from django.contrib.auth.models import User as BaseUser
from .base import models
from . import acl


logger = logging.getLogger("ssansible")


class ACLPermission(acl.ACLPermissionAbstract):
    role = models.CharField(max_length=10)


class UserGroup(BaseGroup, acl.ACLGroupSubclass, acl.ACLPermissionSubclass):
    objects = acl.ACLUserGroupsQuerySet.as_manager()
    parent = models.OneToOneField(BaseGroup, parent_link=True)
    users = BaseGroup.user_set

    def __unicode__(self):
        return super(UserGroup, self).__unicode__()

    @property
    def users_list(self):
        return list(self.users.values_list("id", flat=True))

    @users_list.setter
    def users_list(self, value):
        self.users.set(BaseUser.objects.filter(id__in=value))
