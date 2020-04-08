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
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from rest_framework.serializers import ValidationError
from grafana.models import (Panel,)
from grafana.pagination import CustomPagination
from grafana.exceptions import CustomException
from grafana.serializers import (PanelSerializer,)

logger = logging.getLogger(__name__)


class PanelList(generics.GenericAPIView):
    """
    List all panel objects, or create a new panel.
    """
    pagination_class = CustomPagination
    serializer_class = PanelSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Panel.objects.all().order_by('created_time')
    lookup_field = 'panel_uuid'

    def get(self, request, format=None):
        """
        Get all panel objects.
        """
        queryset = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a panel instance.
        """
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PanelDetail(generics.GenericAPIView):
    """
    Retrieve, update a panel instance.
    """
    permission_classes = (permissions.IsAuthenticated,)
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Panel.DoesNotExist:
            raise CustomException("Not Found the Panel Instance.",
                                  status_code=status.HTTP_404_NOT_FOUND)

    def delete(self, request, panel_uuid):
        panel = self.get_object(panel_uuid)
        panel.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
