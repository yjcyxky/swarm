# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import logging
import uuid
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from grafana.models import (Panel, Dashboard)
from grafana.pagination import CustomPagination
from grafana.exceptions import CustomException
from grafana.serializers import (PanelSerializer, DashboardSerializer)

logger = logging.getLogger(__name__)


class PanelList(generics.GenericAPIView):
    """
    List all panel objects, or create a new panel.
    """
    pagination_class = CustomPagination
    serializer_class = PanelSerializer
    queryset = Panel.objects.all().order_by('created_time')
    lookup_field = 'panel_uuid'
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self, filters=None):
        if filters:
            return Panel.objects.all().filter(**filters)
        else:
            return Panel.objects.all()

    def get(self, request, format=None):
        """
        Get all panel objects.
        """
        query_params = request.query_params
        filters = {}

        db_name = query_params.get('db_name')
        if db_name:
            filters.update({'db_name': db_name})

        panel_type = query_params.get('panel_type')
        if panel_type:
            filters.update({'panel_type': panel_type})

        title = query_params.get('title')
        if title:
            filters.update({'title__icontains': title})

        queryset = self.paginate_queryset(self.get_queryset(filters))
        serializer = self.get_serializer(queryset, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a panel instance.
        """
        request.data.update({'panel_uuid': str(uuid.uuid4())})
        print('Create Panel: %s' % request.data)
        serializer = PanelSerializer(data=request.data,
                                     context={'request': request})
        if serializer.is_valid():
            panel = serializer.create(serializer.validated_data)
            serializer = PanelSerializer(panel, context={'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response({
            'status': 'Bad Request',
            'message': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class PanelDetail(generics.GenericAPIView):
    """
    Retrieve, update a panel instance.
    """
    serializer_class = PanelSerializer
    queryset = Panel.objects
    lookup_field = 'panel_uuid'

    def get_object(self, panel_uuid):
        try:
            return self.queryset.get(panel_uuid=panel_uuid)
        except Panel.DoesNotExist:
            raise CustomException("Not Found the Panel Instance.",
                                  status_code=status.HTTP_404_NOT_FOUND)

    def get(self, request, panel_uuid):
        """
        Retrieve panel information for a specified panel instance.
        """
        panel = self.get_object(panel_uuid)
        serializer = PanelSerializer(panel, context={'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        })

    def put(self, request, panel_uuid):
        """
        Modify panel information.
        """
        try:
            panel = self.get_object(panel_uuid)
            serializer = PanelSerializer(panel, data=request.data,
                                         context={'request': request},
                                         partial=True)
            if serializer.is_valid():
                panel = serializer.update(panel, serializer.validated_data)
                serializer = PanelSerializer(
                    panel, context={'request': request})
                return Response({
                    "status": "Updated Success",
                    "status_code": status.HTTP_200_OK,
                    "data": serializer.data
                })
            return Response({
            'status': 'Bad Request',
            'message': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)
        except Panel.DoesNotExist:
            raise CustomException("Not Found the Panel Instance.",
                                  status_code=status.HTTP_404_NOT_FOUND)

    def delete(self, request, panel_uuid):
        panel = self.get_object(panel_uuid)
        panel.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DashboardList(generics.GenericAPIView):
    """
    List all dashboard objects, or create a new dashboard.
    """
    pagination_class = CustomPagination
    serializer_class = DashboardSerializer
    queryset = Dashboard.objects.all().order_by('created_time')
    lookup_field = 'dashboard_uuid'

    def get_queryset(self, filters=None):
        if filters:
            return Dashboard.objects.all().filter(**filters)
        else:
            return Dashboard.objects.all()

    def get(self, request, format=None):
        """
        Get all dashboard objects.
        """
        query_params = request.query_params
        filters = {}

        title = query_params.get('title')
        if title:
            filters.update({'title__icontains': title})

        queryset = self.paginate_queryset(self.get_queryset(filters))
        serializer = self.get_serializer(queryset, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a dashboard instance.
        """
        request.data.update({'dashboard_uuid': str(uuid.uuid4())})
        serializer = DashboardSerializer(data=request.data,
                                         context={'request': request})
        if serializer.is_valid():
            dashboard = serializer.create(serializer.validated_data)
            serializer = DashboardSerializer(
                dashboard, context={'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response({
            'status': 'Bad Request',
            'message': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class DashboardDetail(generics.GenericAPIView):
    """
    Retrieve, update a dashboard instance.
    """
    serializer_class = DashboardSerializer
    queryset = Dashboard.objects
    lookup_field = 'dashboard_uuid'

    def get_object(self, dashboard_uuid):
        try:
            return self.queryset.get(dashboard_uuid=dashboard_uuid)
        except Dashboard.DoesNotExist:
            raise CustomException("Not Found the Dashboard Instance.",
                                  status_code=status.HTTP_404_NOT_FOUND)

    def get(self, request, dashboard_uuid):
        """
        Retrieve dashboard information for a specified dashboard instance.
        """
        dashboard = self.get_object(dashboard_uuid)
        serializer = DashboardSerializer(
            dashboard, context={'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        })

    def put(self, request, dashboard_uuid):
        """
        Modify dashboard information.
        """
        try:
            dashboard = self.get_object(dashboard_uuid)
            serializer = DashboardSerializer(dashboard, data=request.data,
                                             context={'request': request},
                                             partial=True)
            if serializer.is_valid():
                dashboard = serializer.update(
                    dashboard, serializer.validated_data)
                serializer = DashboardSerializer(
                    dashboard, context={'request': request})
                return Response({
                    "status": "Updated Success",
                    "status_code": status.HTTP_200_OK,
                    "data": serializer.data
                })
            return Response({
            'status': 'Bad Request',
            'message': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)
        except Dashboard.DoesNotExist:
            raise CustomException("Not Found the Dashboard Instance.",
                                  status_code=status.HTTP_404_NOT_FOUND)

    def delete(self, request, dashboard_uuid):
        dashboard = self.get_object(dashboard_uuid)
        dashboard.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
