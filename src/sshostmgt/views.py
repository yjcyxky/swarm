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
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.serializers import ValidationError
from sshostmgt.models import (IPMI, Host, Tag, Storage)
from sshostmgt.pagination import CustomPagination
from sshostmgt.exceptions import CustomException
from sshostmgt.serializers import (IPMISerializer, TagSerializer, StorageSerializer,
                                   HostSerializer, HostListSerializer)

logger = logging.getLogger(__name__)

class IPMIList(generics.GenericAPIView):
    """
    List all ipmi objects, or create a new ipmi.
    """
    pagination_class = CustomPagination
    serializer_class = IPMISerializer
    queryset = IPMI.objects.all().order_by('ipmi_addr')
    lookup_field = 'ipmi_uuid'
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self, filters = None):
        if filters:
            return IPMI.objects.all().filter(**filters)
        else:
            return IPMI.objects.all()

    def get(self, request, format=None):
        """
        Get all ipmi objects.
        """
        query_params = request.query_params
        filters = {}

        ipmi_addr = query_params.get('ipmi_addr')
        if ipmi_addr:
            filters.update({'ipmi_addr': ipmi_addr})

        power_state = query_params.get('power_state')
        if power_state:
            filters.update({'power_state': power_state})

        queryset = self.paginate_queryset(self.get_queryset(filters))
        serializer = self.get_serializer(queryset, many = True,
                                         context = {'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a ipmi instance.
        """
        serializer = IPMISerializer(data=request.data,
                                    context={'request': request})
        if serializer.is_valid():
            ipmi = serializer.create(serializer.validated_data)
            serializer = IPMISerializer(ipmi, context={'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response({
            'status': 'Bad Request',
            'message': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class IPMIDetail(generics.GenericAPIView):
    """
    Retrieve, update a ipmi instance.
    """
    serializer_class = IPMISerializer
    queryset = IPMI.objects
    lookup_field = 'ipmi_uuid'

    def get_object(self, ipmi_uuid):
        try:
            return self.queryset.get(ipmi_uuid=ipmi_uuid)
        except IPMI.DoesNotExist:
            raise CustomException("Not Found the IPMI Instance.",
                                  status_code=status.HTTP_404_NOT_FOUND)

    def get(self, request, ipmi_uuid):
        """
        Retrieve ipmi information for a specified ipmi instance.
        """
        ipmi = self.get_object(ipmi_uuid)
        serializer = IPMISerializer(ipmi, context={'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        })

    def put(self, request, ipmi_uuid):
        """
        Modify ipmi information.
        """
        ipmi = self.get_object(ipmi_uuid)
        serializer = IPMISerializer(ipmi, data=request.data,
                                    context={'request': request},
                                    partial=True)
        if serializer.is_valid():
            power_state = serializer.validated_data.get('power_state')
            ipmi = serializer.update_power_state(ipmi, power_state)
            serializer = IPMISerializer(ipmi, context={'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response({
            'status': 'Bad Request',
            'message': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, ipmi_uuid, format=None):
        ipmi = self.get_object(ipmi_uuid)
        ipmi.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagList(generics.GenericAPIView):
    """
    List all tag objects, or create a new tag.
    """
    pagination_class = CustomPagination
    serializer_class = TagSerializer
    queryset = Tag.objects.all().order_by('tag_name')
    lookup_field = 'tag_uuid'
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self, filters = None):
        if filters:
            return Tag.objects.all().filter(**filters)
        else:
            return Tag.objects.all()

    def get(self, request, format=None):
        """
        Get all tag objects.
        """
        query_params = request.query_params
        filters = {}

        tag_name = query_params.get('tag_name')
        if tag_name:
            filters.update({'tag_name__icontains': tag_name})

        queryset = self.paginate_queryset(self.get_queryset(filters))
        serializer = self.get_serializer(queryset, many = True,
                                         context = {'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a tag instance.
        """
        serializer = TagSerializer(data=request.data,
                                   context={'request': request})
        if serializer.is_valid():
            tag = serializer.create(serializer.validated_data)
            serializer = TagSerializer(tag, context={'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response({
            'status': 'Bad Request',
            'message': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class TagDetail(generics.GenericAPIView):
    """
    Retrieve, update a tag instance.
    """
    serializer_class = TagSerializer
    queryset = Tag.objects
    lookup_field = 'tag_uuid'

    def get_object(self, tag_uuid):
        try:
            return self.queryset.get(tag_uuid=tag_uuid)
        except Tag.DoesNotExist:
            raise CustomException("Not Found the Tag Instance.",
                                  status_code=status.HTTP_404_NOT_FOUND)

    def get(self, request, tag_uuid):
        """
        Retrieve tag information for a specified tag instance.
        """
        tag = self.get_object(tag_uuid)
        serializer = TagSerializer(tag, context={'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        })

    def put(self, request, tag_uuid):
        """
        Modify tag information.
        """
        tag = self.get_object(tag_uuid)
        serializer = TagSerializer(tag, data=request.data,
                                   context={'request': request},
                                   partial=True)
        if serializer.is_valid():
            tag = serializer.update(tag, serializer.validated_data)
            serializer = TagSerializer(tag, context={'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response({
            'status': 'Bad Request',
            'message': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class HostList(generics.GenericAPIView):
    """
    List all host objects, or create a new host.
    """
    pagination_class = CustomPagination
    serializer_class = HostListSerializer
    queryset = Host.objects.all().order_by('hostname')
    lookup_field = 'host_uuid'
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self, filters = None):
        if filters:
            return Host.objects.all().filter(**filters)
        else:
            return Host.objects.all()

    def get(self, request, format=None):
        """
        Get all host objects.
        """
        query_params = request.query_params
        filters = {}

        mgmt_mac = query_params.get('mgmt_mac')
        if mgmt_mac:
            filters.update({'mgmt_mac': mgmt_mac})

        hostname = query_params.get('hostname')
        if hostname:
            filters.update({'hostname': hostname})

        mgmt_ip_addr = query_params.get('mgmt_ip_addr')
        if mgmt_ip_addr:
            filters.update({'mgmt_ip_addr': mgmt_ip_addr})

        queryset = self.paginate_queryset(self.get_queryset(filters))
        serializer = self.get_serializer(queryset, many = True,
                                         context = {'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a host instance.
        """
        serializer = HostSerializer(data=request.data,
                                    context={'request': request})
        if serializer.is_valid():
            host = serializer.create(serializer.validated_data)
            serializer = HostSerializer(host, context={'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response({
            'status': 'Bad Request',
            'message': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class HostDetail(generics.GenericAPIView):
    """
    Retrieve, update a host instance.
    """
    serializer_class = HostSerializer
    queryset = Host.objects
    lookup_field = 'host_uuid'

    def get_object(self, host_uuid):
        try:
            return self.queryset.get(host_uuid=host_uuid)
        except Host.DoesNotExist:
            raise CustomException("Not Found the Host Instance.",
                                  status_code=status.HTTP_404_NOT_FOUND)

    def get(self, request, host_uuid):
        """
        Retrieve host information for a specified host instance.
        """
        host = self.get_object(host_uuid)
        serializer = HostSerializer(host, context={'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        })

    def put(self, request, host_uuid):
        """
        Modify host information.
        """
        host = self.get_object(host_uuid)
        serializer = HostSerializer(host, data=request.data,
                                    context={'request': request},
                                    partial=True)
        if serializer.is_valid():
            try:
                serializer.update(host, serializer.validated_data)
            except ValidationError as err:
                raise CustomException(str(err),
                                      status_code=status.HTTP_400_BAD_REQUEST)
            serializer = HostSerializer(host, context={'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response({
            'status': 'Bad Request',
            'message': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, host_uuid, format=None):
        host = self.get_object(host_uuid)
        ipmi = host.ipmi
        host.delete()
        ipmi.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StorageList(generics.GenericAPIView):
    """
    List all storage objects, or create a new storage.
    """
    pagination_class = CustomPagination
    serializer_class = StorageSerializer
    queryset = Storage.objects.all().order_by('storage_name')
    lookup_field = 'storage_uuid'
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self, filters = None):
        if filters:
            return Storage.objects.all().filter(**filters)
        else:
            return Storage.objects.all()

    def get(self, request, format=None):
        """
        Get all storage objects.
        """
        query_params = request.query_params
        filters = {}

        storage_name = query_params.get('storage_name')
        if storage_name:
            filters.update({'storage_name': storage_name})

        queryset = self.paginate_queryset(self.get_queryset(filters))
        serializer = self.get_serializer(queryset, many = True,
                                         context = {'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a storage instance.
        """
        serializer = StorageSerializer(data=request.data,
                                       context={'request': request})
        if serializer.is_valid():
            storage = serializer.create(serializer.validated_data)
            serializer = StorageSerializer(storage,
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


class StorageDetail(generics.GenericAPIView):
    """
    Retrieve, update a storage instance.
    """
    serializer_class = StorageSerializer
    queryset = Storage.objects
    lookup_field = 'storage_uuid'

    def get_object(self, storage_uuid):
        try:
            return self.queryset.get(storage_uuid=storage_uuid)
        except Storage.DoesNotExist:
            raise CustomException("Not Found the Storage Instance.",
                                  status_code=status.HTTP_404_NOT_FOUND)

    def get(self, request, storage_uuid):
        """
        Retrieve storage information for a specified storage instance.
        """
        storage = self.get_object(storage_uuid)
        serializer = StorageSerializer(storage, context={'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        })

    def put(self, request, storage_uuid):
        """
        Modify storage information.
        """
        storage = self.get_object(storage_uuid)
        serializer = StorageSerializer(storage, data=request.data,
                                       context={'request': request},
                                       partial=True)
        if serializer.is_valid():
            serializer.update(storage, serializer.validated_data)
            serializer = StorageSerializer(storage,
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
