# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import logging
import time
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from ssganglia.pagination import CustomPagination
from ssganglia.exceptions import CustomException
from ssganglia.serializers import RRDSerializer, RRDConfigSerializer
from ssganglia.models import RRDConfigModel, RRDData

logger = logging.getLogger(__name__)


class ClusterList(generics.GenericAPIView):
    """
    List all clusters.
    """
    permission_classes = (permissions.IsAuthenticated,
                          permissions.IsAdminUser)
    pagination_class = CustomPagination
    serializer_class = RRDConfigSerializer

    queryset = RRDConfigModel.objects.all().order_by('clustername')

    def get(self, request, format=None):
        """
        Get all clusters.
        """
        queryset = self.paginate_queryset(self.queryset)
        serializer = self.get_serializer(queryset, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a cluster instance.
        """
        serializer = RRDConfigSerializer(data=request.data,
                                         context={'request': request})
        if serializer.is_valid():
            rrd_config = serializer.create(serializer.validated_data)
            serializer = RRDConfigSerializer(rrd_config,
                                             context={'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class HostList(generics.GenericAPIView):
    """
    List all hosts.
    """
    permission_classes = (permissions.IsAuthenticated,
                          permissions.IsAdminUser)
    pagination_class = CustomPagination
    serializer_class = RRDConfigSerializer

    queryset = RRDConfigModel.objects.all().order_by('hostname')

    def get_queryset(self, clustername):
        try:
            return self.queryset.filter(clustername=clustername)
        except RRDConfigModel.DoesNotExist:
            raise CustomException("Not Found the Cluster.",
                                  status_code=status.HTTP_404_NOT_FOUND)

    def get(self, request, clustername, format=None):
        """
        Get all hosts.
        """
        queryset = self.paginate_queryset(self.get_queryset(clustername))
        serializer = self.get_serializer(queryset, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)


class MetricList(generics.GenericAPIView):
    """
    List all metrics.
    """
    permission_classes = (permissions.IsAuthenticated,
                          permissions.IsAdminUser)
    pagination_class = CustomPagination
    serializer_class = RRDConfigSerializer

    queryset = RRDConfigModel.objects.all().order_by('metric')

    def get_queryset(self, hostname):
        try:
            return self.queryset.filter(hostname=hostname)
        except RRDConfigModel.DoesNotExist:
            raise CustomException("Not Found the Host.",
                                  status_code=status.HTTP_404_NOT_FOUND)

    def get(self, request, hostname, format=None):
        """
        Get all hosts.
        """
        queryset = self.paginate_queryset(self.get_queryset(hostname))
        serializer = self.get_serializer(queryset, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)


class MetricDetail(generics.GenericAPIView):
    """
    Get Metric Information.
    """
    permission_classes = (permissions.IsAuthenticated,
                          permissions.IsAdminUser)
    serializer_class = RRDSerializer
    queryset = RRDConfigModel.objects.all().order_by('metric')

    def get_object(self, hostname, metric):
        try:
            return self.queryset.get(hostname=hostname, metric=metric)
        except RRDConfigModel.DoesNotExist:
            raise CustomException("Not Found the Metric.",
                                  status_code=status.HTTP_404_NOT_FOUND)

    def get(self, request, hostname, metric):
        """
        Retrieve metric information for a specified metric instance.
        """
        query_params = request.query_params
        try:
            start = query_params.get('start', 0)
            end = query_params.get('end', 'now')
            # The unit of resolution is minute.
            resolution = query_params.get('resolution', 1)
            cf = query_params.get('cf', 'AVERAGE')
            if cf not in ('AVERAGE', 'MIN', 'MAX', 'LAST'):
                raise CustomException("cf must be one of 'AVERAGE', 'MIN', \
                                       'MAX' and 'LAST'",
                                      status_code=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            raise CustomException("Invalid query parameters.",
                                  status_code=status.HTTP_400_BAD_REQUEST)

        metric = self.get_object(hostname, metric)
        filename = metric.filename
        rrd_instance = RRDData(filename)
        rrd_meta, rrd_data = rrd_instance.fetch_data(start=start, end=end,
                                                     resolution=resolution,
                                                     cf=cf)
        serializer = RRDSerializer(rrd_data, many=True,
                                   context={'request': request})
        rrd_meta_serializer = RRDConfigSerializer(rrd_meta,
                                                  context={'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data,
            "metadata": rrd_meta_serializer.data
        })
