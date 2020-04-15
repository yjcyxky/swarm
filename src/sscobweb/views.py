# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import logging
from django.http import Http404
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from sscobweb.models import (Channel, Package, CobwebSetting)
from sscobweb.pagination import CustomPagination
from sscobweb.exceptions import CustomException
from sscobweb.serializers import (ChannelSerializer, PackageSerializer, SettingSerializer)
from sscobweb.conda import Channel as ChannelImporter
from sscobweb.conda import Conda
from django.db import connection

logger = logging.getLogger(__name__)


class ChannelList(generics.GenericAPIView):
    """
    List all channel objects, or create a channel instance.
    """
    pagination_class = CustomPagination
    serializer_class = ChannelSerializer
    queryset = Channel.objects.all().order_by('is_active')
    lookup_field = 'channel_uuid'
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self, filters = None):
        if filters:
            return Channel.objects.all().filter(**filters)
        else:
            return Channel.objects.all()

    def get(self, request, format=None):
        """
        Get all channel objects.
        """
        query_params = request.query_params
        filters = {}

        channel_name = query_params.get('channel_name')
        if channel_name:
            filters.update({'channel_name__icontains': channel_name})

        queryset = self.paginate_queryset(self.get_queryset(filters))
        serializer = self.get_serializer(queryset, many = True,
                                         context = {'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a channel instance.
        """
        serializer = ChannelSerializer(data=request.data,
                                       context={'request': request})
        if serializer.is_valid():
            validated_data = serializer.validated_data
            channel_name = validated_data.get('channel_name')
            channel_path = validated_data.get('channel_path')
            channel_importer = ChannelImporter(channel_name, channel_path)
            channel_importer.fetch_repodata()
            channel_importer.sync()
            # channel = serializer.create(serializer.validated_data)
            channel_name = validated_data.get('channel_name')
            channel = self.get_object(channel_name=channel_name)
            serializer = ChannelSerializer(channel,
                                           context={'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response({
            'status': 'Bad Request',
            'message': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class ChannelDetail(generics.GenericAPIView):
    """
    Retrieve, update a channel instance.
    """
    serializer_class = ChannelSerializer
    queryset = Channel.objects
    lookup_field = 'channel_uuid'

    def get_object(self, channel_uuid):
        try:
            return self.queryset.get(channel_uuid=channel_uuid)
        except Channel.DoesNotExist:
            raise CustomException("Not Found the Channel.",
                                  status_code=status.HTTP_404_NOT_FOUND)

    def get(self, request, channel_uuid):
        """
        Retrieve channel information for a specified channel instance.
        """
        channel = self.get_object(channel_uuid)
        serializer = ChannelSerializer(channel, context={'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        })

    def put(self, request, channel_uuid):
        """
        Modify channel information.
        """
        channel = self.get_object(channel_uuid)
        serializer = ChannelSerializer(channel, data=request.data,
                                       context={'request': request},
                                       partial=True)
        query_params = request.query_params
        if serializer.is_valid():
            logger.debug(query_params.get('update_repodata'))
            if query_params.get('update_repodata', 'False').upper() == 'TRUE':
                validated_data = serializer.data
                channel_name = validated_data.get('channel_name')
                channel_path = validated_data.get('channel_path')
                channel_importer = ChannelImporter(channel_name, channel_path)
                channel_importer.fetch_repodata()
                channel_importer.sync()

            channel = serializer.update(channel, serializer.validated_data)
            serializer = ChannelSerializer(channel,
                                           context={'request': request})

            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_200_OK)


class PackageList(generics.GenericAPIView):
    """
    List all package objects, or create a new package.
    """
    pagination_class = CustomPagination
    serializer_class = PackageSerializer
    queryset = Package.objects.all().order_by('pkg_name')
    lookup_field = 'pkg_uuid'
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self, filters=None):
        if filters:
            return Package.objects.all()\
                          .filter(**filters)\
                          .order_by('pkg_name', 'is_installed')
        else:
            return Package.objects.all()\
                          .order_by('pkg_name', 'is_installed')

    def get(self, request, format=None):
        """
        Get all package objects.
        """
        query_params = request.query_params

        filters = {}
        name = query_params.get('name', '')
        name = name if len(name) > 0 else None
        is_installed = query_params.get('is_installed')
        installed_time = query_params.get('installed_time',
                                            '2100-12-12 08:00:00')
        created_date = query_params.get('created_date')
        if created_date:
            filters.update({
                'created_date__gt': created_date,
            })
        if is_installed:
            filters.update({
                'is_installed': bool(is_installed),
                'installed_time__lt': installed_time,
            })
        if name:
            filters.update({
                'name__contains': name
            })

        queryset = self.paginate_queryset(self.get_queryset(filters))
        serializer = self.get_serializer(queryset, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a package instance.
        """
        serializer = PackageSerializer(data=request.data,
                                       context={'request': request})
        if serializer.is_valid():
            package = serializer.create(serializer.validated_data)
            serializer = PackageSerializer(package,
                                           context={'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response({
            'status': 'Bad Request',
            'message': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class PackageDetail(generics.GenericAPIView):
    """
    Retrieve, update a package instance.
    """
    serializer_class = PackageSerializer
    queryset = Package.objects
    lookup_field = 'pkg_uuid'

    def get_object(self, pkg_uuid):
        try:
            return self.queryset.get(pkg_uuid=pkg_uuid)
        except Package.DoesNotExist:
            raise CustomException("Not Found the Package.",
                                  status_code=status.HTTP_404_NOT_FOUND)

    def get(self, request, pkg_uuid):
        """
        Retrieve package information for a specified package instance.
        """
        package = self.get_object(pkg_uuid)
        serializer = PackageSerializer(package, context={'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        })

    def put(self, request, pkg_uuid):
        """
        Modify package information.
        """
        package = self.get_object(pkg_uuid=pkg_uuid)
        serializer = PackageSerializer(package, data=request.data,
                                       context={'request': request},
                                       partial=True)
        query_params = request.query_params
        if serializer.is_valid():
            if query_params.get('install_pkg', 'False').upper() == 'TRUE':
                pkg_uuid = package.pkg_uuid
                conda = Conda(pkg_uuid=pkg_uuid)
                conda.reset_channels()
                package = conda.install()
            elif query_params.get('remove_pkg', 'False').upper() == 'TRUE':
                pkg_uuid = package.pkg_uuid
                conda = Conda(pkg_uuid=pkg_uuid)
                package = conda.remove()
            else:
                package = serializer.update(package, serializer.validated_data)

            serializer = PackageSerializer(package,
                                           context={'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response({
            'status': 'Bad Request',
            'message': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class SettingList(generics.GenericAPIView):
    """
    List all setting objects, or create a new setting.
    """
    pagination_class = CustomPagination
    serializer_class = SettingSerializer
    queryset = CobwebSetting.objects.all().order_by('name')
    lookup_field = 'setting_uuid'
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self, filters=None):
        try:
            if filters:
                return CobwebSetting.objects.all()\
                                            .filter(**filters)\
                                            .order_by('name', 'is_active')
            else:
                return CobwebSetting.objects.all()\
                                            .order_by('name', 'is_active')
        except CobwebSetting.DoesNotExist:
            raise CustomException("Not Found the Settings.",
                                  status_code=status.HTTP_404_NOT_FOUND)

    def get(self, request, format=None):
        """
        Get all setting objects.
        """
        query_params = request.query_params

        filters = {}
        is_active = query_params.get('is_active')
        cobweb_root_prefix = query_params.get('cobweb_root_prefix')
        cobweb_platform = query_params.get('cobweb_platform')
        cobweb_arch = query_params.get('cobweb_arch')
        cobweb_home = query_params.get('cobweb_home')
        if is_active:
            filters.update({
                'is_active': True if is_active.upper() == 'TRUE' else False,
            })
        if cobweb_root_prefix:
            filters.update({
                'cobweb_root_prefix': cobweb_root_prefix
            })
        if cobweb_platform:
            filters.update({
                'cobweb_platform': cobweb_platform
            })
        if cobweb_arch:
            filters.update({
                'cobweb_arch': cobweb_arch
            })
        if cobweb_home:
            filters.update({
                'cobweb_home': cobweb_home
            })

        queryset = self.paginate_queryset(self.get_queryset(filters))
        serializer = self.get_serializer(queryset, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a setting instance.
        """
        serializer = SettingSerializer(data=request.data,
                                       context={'request': request})
        if serializer.is_valid():
            setting = serializer.create(serializer.validated_data)
            serializer = SettingSerializer(setting,
                                           context={'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response({
            'status': 'Bad Request',
            'message': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class SettingDetail(generics.GenericAPIView):
    """
    Retrieve, update a setting instance.
    """
    serializer_class = SettingSerializer
    queryset = CobwebSetting.objects
    lookup_field = 'setting_uuid'

    def get_object(self, setting_uuid):
        try:
            return self.queryset.get(setting_uuid=setting_uuid)
        except CobwebSetting.DoesNotExist:
            raise CustomException("Not Found the Setting.",
                                  status_code=status.HTTP_404_NOT_FOUND)

    def get(self, request, setting_uuid):
        """
        Retrieve setting information for a specified setting instance.
        """
        setting = self.get_object(setting_uuid)
        serializer = SettingSerializer(setting, context={'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        })

    def put(self, request, setting_uuid):
        """
        Modify setting information.
        """
        setting = self.get_object(setting_uuid=setting_uuid)
        serializer = SettingSerializer(setting, data=request.data,
                                       context={'request': request},
                                       partial=True)
        if serializer.is_valid():
            setting = serializer.update(setting, serializer.validated_data)
            serializer = SettingSerializer(setting,
                                           context={'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response({
            'status': 'Bad Request',
            'message': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)
