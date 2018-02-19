# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import logging
from rest_framework import generics
from rest_framework import permissions
from ssnagios.pagination import CustomPagination
from ssnagios.serializers import NotificationsSerializer
from ssnagios.models import Notifications

logger = logging.getLogger(__name__)


class NotificationList(generics.GenericAPIView):
    """
    List all notifications.
    """
    permission_classes = (permissions.IsAuthenticated,
                          permissions.IsAdminUser)
    pagination_class = CustomPagination
    serializer_class = NotificationsSerializer

    queryset = Notifications.objects.all().order_by('checked')

    def get(self, request, format=None):
        """
        Get all notifications.
        """
        queryset = self.paginate_queryset(self.queryset)
        serializer = self.get_serializer(queryset, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)
