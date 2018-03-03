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
from rest_framework import status
from rest_framework.response import Response
from ssnagios.exceptions import CustomException
from ssnagios.pagination import CustomPagination
from ssnagios.serializers import NotificationsSerializer, HostsSerializer
from ssnagios.models import Notifications, Hosts

logger = logging.getLogger(__name__)


class NotificationList(generics.GenericAPIView):
    """
    List all notifications.
    """
    permission_classes = (permissions.IsAuthenticated,
                          permissions.IsAdminUser)
    pagination_class = CustomPagination
    serializer_class = NotificationsSerializer

    queryset = Notifications.objects.all().order_by('-start_time', 'checked')

    def get(self, request, format=None):
        """
        Get all notifications.
        """
        query_params = request.query_params
        checked = query_params.get('checked')
        if checked:
            checked = checked if isinstance(checked, int) else 0
            checked = int(checked)
            queryset = self.queryset.filter(checked=checked)
        else:
            queryset = self.queryset
        queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)


class NotificationDetail(generics.GenericAPIView):
    """
    Retrieve, update a notification instance.
    """
    permission_classes = (permissions.IsAuthenticated,
                          permissions.IsAdminUser)
    serializer_class = NotificationsSerializer
    queryset = Notifications.objects.all().order_by('-start_time')
    lookup_field = 'notification_id'

    def get_object(self, notification_id):
        try:
            return self.queryset.get(notification_id=notification_id)
        except Notifications.DoesNotExist:
            raise CustomException("Not Found the Notification.",
                                  status_code=status.HTTP_404_NOT_FOUND)

    def get(self, request, notification_id):
        """
        Retrieve the information for a specified notification instance.
        """
        notification = self.get_object(notification_id)
        serializer = NotificationsSerializer(notification,
                                             context={'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        })

    def put(self, request, notification_id):
        """
        Modify notification information.
        """
        notification = self.get_object(notification_id)
        serializer = NotificationsSerializer(notification, data=request.data,
                                             context={'request': request},
                                             partial=True)
        if serializer.is_valid():
            notification = serializer.update(notification,
                                             serializer.validated_data)
            serializer = NotificationsSerializer(notification,
                                                 context={'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_200_OK)


class HostDetail(generics.GenericAPIView):
    """
    Get Nagios Host Information.
    """
    permission_classes = (permissions.IsAuthenticated,
                          permissions.IsAdminUser)
    pagination_class = CustomPagination
    serializer_class = HostsSerializer

    queryset = Hosts.objects.all()

    def get_object(self, hostname):
        try:
            return self.queryset.get(alias=hostname)
        except Hosts.DoesNotExist:
            raise CustomException("Not Found the Host.",
                                  status_code=status.HTTP_404_NOT_FOUND)

    def get(self, request, hostname):
        """
        Retrieve host information for a specified host instance.
        """
        host = self.get_object(hostname)
        serializer = HostsSerializer(host, context={'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        })
