import logging
import django_filters.rest_framework
from django.http import Http404
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from sscobweb.models import (Channel, Package)
from sscobweb.pagination import CustomPagination
from sscobweb.permissions import IsOwnerOrAdmin
from sscobweb.exceptions import CustomException
from sscobweb.serializers import (ChannelSerializer, PackageSerializer)
from sscobweb.utils import Channel as ChannelImporter
from django.db import connection

logger = logging.getLogger(__name__)

class ChannelList(generics.GenericAPIView):
    """
    List all channel objects, or create a channel instance.
    """
    pagination_class = CustomPagination
    serializer_class = ChannelSerializer
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.DjangoModelPermissions,
    #                       permissions.IsAdminUser)
    queryset = Channel.objects.all().order_by('is_active')
    lookup_field = 'channel_uuid'

    def exist_object(self, **kwargs):
        new_kwargs = {}
        for key in kwargs.keys():
            if key in ('channel_uuid', 'channel_name', 'md5sum'):
                if len(kwargs.get(key)) > 1:
                    return False
                else:
                    new_kwargs[key] = kwargs.get(key)[0]

        if new_kwargs:
            try:
                logger.debug("ChannelList@exist_object@new_kwargs:%s" % str(new_kwargs))
                logger.debug("ChannelList@exist_object@objects:%s" % str(self.queryset.get(**new_kwargs)))
                return self.queryset.get(**new_kwargs)
            except Channel.DoesNotExist:
                return False

    def get_object(self, channel_name):
        try:
            return self.queryset.get(channel_name = channel_name)
        except Channel.DoesNotExist:
            raise CustomException("Not Found the Channel.", status_code = status.HTTP_200_OK)

    def get(self, request, format = None):
        """
        Get all channel objects.
        """
        query_params = request.query_params
        if query_params and (query_params.get('channel_uuid') or \
                             query_params.get('channel_name') or \
                             query_params.get('md5sum')):
            if not self.exist_object(**query_params):
                return Response({
                    "status": "Not Found.",
                    "status_code": status.HTTP_404_NOT_FOUND,
                    "data": []
                })
            else:
                return Response({
                    "status": "Success.",
                    "status_code": status.HTTP_200_OK
                })
        else:
            queryset = self.paginate_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many = True,
                                             context = {'request': request})
            return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a channel instance.
        """
        serializer = ChannelSerializer(data = request.data,
                                       context = {'request': request})
        if serializer.is_valid():
            validated_data = serializer.validated_data
            channel_name = validated_data.get('channel_name')
            channel_path = validated_data.get('channel_path')
            dest_dir = '/Users/FK/Downloads/Test'
            channel_importer = ChannelImporter(channel_name, channel_path, dest_dir)
            channel_importer.fetch_repodata()
            channel_importer.sync()
            # channel = serializer.create(serializer.validated_data)
            channel = self.get_object(channel_name = validated_data.get('channel_name'))
            serializer = ChannelSerializer(channel, context = {'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class ChannelDetail(generics.GenericAPIView):
    """
    Retrieve, update a channel instance.
    """
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.IsAdminUser)
    serializer_class = ChannelSerializer
    queryset = Channel.objects
    lookup_field = 'channel_uuid'

    def get_object(self, channel_uuid):
        try:
            return self.queryset.get(channel_uuid = channel_uuid)
        except Channel.DoesNotExist:
            raise CustomException("Not Found the Channel.", status_code = status.HTTP_200_OK)

    def get(self, request, channel_uuid):
        """
        Retrieve channel information for a specified channel instance.
        """
        channel = self.get_object(channel_uuid)
        serializer = ChannelSerializer(channel, context = {'request': request})
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
        serializer = ChannelSerializer(channel, data = request.data,
                                       context = {'request': request},
                                       partial = True)
        query_params = request.query_params
        if serializer.is_valid():
            channel = serializer.update(channel, serializer.validated_data)
            serializer = ChannelSerializer(channel, context = {'request': request})
            logger.debug(query_params.get('update_repodata'))
            if query_params.get('update_repodata', 'False').upper() == 'TRUE':
                validated_data = serializer.data
                channel_name = validated_data.get('channel_name')
                channel_path = validated_data.get('channel_path')
                dest_dir = '/Users/FK/Downloads/Test'
                channel_importer = ChannelImporter(channel_name, channel_path, dest_dir)
                channel_importer.fetch_repodata()
                channel_importer.sync()
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_200_OK)


class PackageList(generics.GenericAPIView):
    """
    List all package objects, or create a new package.
    """
    pagination_class = CustomPagination
    serializer_class = PackageSerializer
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.DjangoModelPermissions,
    #                       permissions.IsAdminUser)
    queryset = Package.objects.all().order_by('pkg_name')
    lookup_field = 'pkg_uuid'
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    def get_queryset(self, filters):
        try:
            return Package.objects.all().filter(**filters).order_by('pkg_name', 'is_installed')
        except Package.DoesNotExist:
            raise CustomException("Not Found the Packages.", status_code = status.HTTP_200_OK)

    def get(self, request, format = None):
        """
        Get all package objects.
        """
        query_params = request.query_params

        try:
            filters = {}
            name = query_params.get('name')
            is_installed = query_params.get('is_installed')
            installed_time = query_params.get('installed_time', '2100-12-12 08:00:00')
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
        except ValueError:
            raise CustomException("Bad Request.", status_code = status.HTTP_200_OK)

        queryset = self.paginate_queryset(self.get_queryset(filters))
        serializer = self.get_serializer(queryset, many = True,
                                         context = {'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a package instance.
        """
        serializer = PackageSerializer(data = request.data,
                                       context = {'request': request})
        if serializer.is_valid():
            package = serializer.create(serializer.validated_data)
            serializer = PackageSerializer(package, context = {'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class PackageDetail(generics.GenericAPIView):
    """
    Retrieve, update a package instance.
    """
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.IsAdminUser)
    serializer_class = PackageSerializer
    queryset = Package.objects
    lookup_field = 'pkg_uuid'

    def get_object(self, pk):
        try:
            return self.queryset.get(pk = pk)
        except Package.DoesNotExist:
            raise CustomException("Not Found the Package.", status_code = status.HTTP_200_OK)

    def get(self, request, pk):
        """
        Retrieve package information for a specified package instance.
        """
        package = self.get_object(pk)
        serializer = PackageSerializer(package, context = {'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        })

    def put(self, request, pk):
        """
        Modify package information.
        """
        package = self.get_object(pk = pk)
        serializer = PackageSerializer(package, data = request.data,
                                       context = {'request': request},
                                       partial = True)
        if serializer.is_valid():
            package = serializer.update(package, serializer.validated_data)
            serializer = PackageSerializer(package, context = {'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
