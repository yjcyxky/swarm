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
from rest_framework.serializers import ValidationError
from sshostmgt.models import (IPMI, Host, Tag, Storage)
from sshostmgt.pagination import CustomPagination
from sshostmgt.permissions import IsOwnerOrAdmin
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
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.DjangoModelPermissions,
    #                       permissions.IsAdminUser)
    queryset = IPMI.objects.all().order_by('ipmi_addr')
    lookup_field = 'ipmi_uuid'

    def exist_object(self, **kwargs):
        new_kwargs = {}
        for key in kwargs.keys():
            if key in ('ipmi_uuid', 'ipmi_mac', 'ipmi_addr'):
                if len(kwargs.get(key)) > 1:
                    return False
                else:
                    new_kwargs[key] = kwargs.get(key)[0]

        if new_kwargs:
            try:
                logger.debug("IPMIList@exist_object@new_kwargs:%s" % str(new_kwargs))
                logger.debug("IPMIList@exist_object@objects:%s" % str(self.queryset.get(**new_kwargs)))
                return self.queryset.get(**new_kwargs)
            except IPMI.DoesNotExist:
                return False

    def get(self, request, format = None):
        """
        Get all ipmi objects.
        """
        query_params = request.query_params
        if query_params and (query_params.get('ipmi_addr') or \
                             query_params.get('ipmi_uuid') or \
                             query_params.get('ipmi_mac')):
            if not self.exist_object(**query_params):
                # raise Http404
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
        Create a ipmi instance.
        """
        serializer = IPMISerializer(data = request.data,
                                    context = {'request': request})
        if serializer.is_valid():
            ipmi = serializer.create(serializer.validated_data)
            serializer = IPMISerializer(ipmi, context = {'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
        Modify ipmi information.
        """
        try:
            ipmi_addr = request.data.get("ipmi_addr")
            if ipmi_addr is None:
                raise CustomException("You need to set ipmi_addr in post.",
                                      status_code = status.HTTP_400_BAD_REQUEST)
            ipmi = self.queryset.get(ipmi_addr = ipmi_addr)
            serializer = IPMISerializer(ipmi, data = request.data,
                                        context = {'request': request},
                                        partial = True)
            if serializer.is_valid():
                ipmi = serializer.update(ipmi, serializer.validated_data)
                serializer = IPMISerializer(ipmi, context = {'request': request})
                return Response({
                    "status": "Updated Success",
                    "status_code": status.HTTP_200_OK,
                    "data": serializer.data
               })
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        except IPMI.DoesNotExist:
            raise CustomException("Not Found the IPMI Instance.", status_code = status.HTTP_404_NOT_FOUND)


class IPMIDetail(generics.GenericAPIView):
    """
    Retrieve, update a ipmi instance.
    """
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.IsAdminUser)
    serializer_class = IPMISerializer
    queryset = IPMI.objects
    lookup_field = 'ipmi_uuid'

    def get_object(self, ipmi_uuid):
        try:
            return self.queryset.get(ipmi_uuid = ipmi_uuid)
        except IPMI.DoesNotExist:
            raise CustomException("Not Found the IPMI Instance.", status_code = status.HTTP_404_NOT_FOUND)

    def get(self, request, ipmi_uuid):
        """
        Retrieve ipmi information for a specified ipmi instance.
        """
        ipmi = self.get_object(ipmi_uuid)
        serializer = IPMISerializer(ipmi, context = {'request': request})
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
        serializer = IPMISerializer(ipmi, data = request.data,
                                    context = {'request': request},
                                    partial = True)
        if serializer.is_valid():
            power_state = serializer.validated_data.get('power_state')
            ipmi = serializer.update_power_state(ipmi, power_state)
            serializer = IPMISerializer(ipmi, context = {'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

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
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.DjangoModelPermissions,
    #                       permissions.IsAdminUser)
    queryset = Tag.objects.all().order_by('tag_name')
    lookup_field = 'tag_uuid'

    def get(self, request, format = None):
        """
        Get all tag objects.
        """
        queryset = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many = True,
                                    context = {'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a tag instance.
        """
        serializer = TagSerializer(data = request.data,
                                   context = {'request': request})
        if serializer.is_valid():
            tag = serializer.create(serializer.validated_data)
            serializer = TagSerializer(tag, context = {'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class TagDetail(generics.GenericAPIView):
    """
    Retrieve, update a tag instance.
    """
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.IsAdminUser)
    serializer_class = TagSerializer
    queryset = Tag.objects
    lookup_field = 'tag_uuid'

    def get_object(self, tag_uuid):
        try:
            return self.queryset.get(tag_uuid = tag_uuid)
        except Tag.DoesNotExist:
            raise CustomException("Not Found the Tag Instance.", status_code = status.HTTP_404_NOT_FOUND)

    def get(self, request, tag_uuid):
        """
        Retrieve tag information for a specified tag instance.
        """
        tag = self.get_object(tag_uuid)
        serializer = TagSerializer(tag, context = {'request': request})
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
        serializer = TagSerializer(tag, data = request.data,
                                   context = {'request': request},
                                   partial = True)
        if serializer.is_valid():
            tag = serializer.update(tag, serializer.validated_data)
            serializer = TagSerializer(tag, context = {'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class HostList(generics.GenericAPIView):
    """
    List all host objects, or create a new host.
    """
    pagination_class = CustomPagination
    serializer_class = HostListSerializer
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.DjangoModelPermissions,
    #                       permissions.IsAdminUser)
    queryset = Host.objects.all().order_by('hostname')
    lookup_field = 'host_uuid'

    def exist_object(self, **kwargs):
        new_kwargs = {}
        for key in kwargs.keys():
            if key in ('host_uuid', 'mgmt_mac', 'mgmt_ip_addr', 'hostname'):
                if len(kwargs.get(key)) > 1:
                    return False
                else:
                    new_kwargs[key] = kwargs.get(key)[0]

        if new_kwargs:
            try:
                logger.debug("HostList@exist_object@new_kwargs:%s" % str(new_kwargs))
                logger.debug("HostList@exist_object@objects:%s" % str(self.queryset.get(**new_kwargs)))
                return self.queryset.get(**new_kwargs)
            except Host.DoesNotExist:
                return False

    def get(self, request, format = None):
        """
        Get all host objects.
        """
        query_params = request.query_params
        if query_params and (query_params.get('mgmt_ip_addr') or \
                             query_params.get('host_uuid') or \
                             query_params.get('mgmt_mac') or \
                             query_params.get('hostname')):
            if not self.exist_object(**query_params):
                return Response({
                    "status": "Failed.",
                    "status_code": status.HTTP_404_NOT_FOUND
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
        Create a host instance.
        """
        serializer = HostSerializer(data = request.data,
                                    context = {'request': request})
        if serializer.is_valid():
            host = serializer.create(serializer.validated_data)
            serializer = HostSerializer(host, context = {'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class HostDetail(generics.GenericAPIView):
    """
    Retrieve, update a host instance.
    """
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.IsAdminUser)
    serializer_class = HostSerializer
    queryset = Host.objects
    lookup_field = 'host_uuid'
    def get_object(self, host_uuid):
        try:
            return self.queryset.get(host_uuid = host_uuid)
        except Host.DoesNotExist:
            raise CustomException("Not Found the Host Instance.", status_code = status.HTTP_404_NOT_FOUND)

    def get(self, request, host_uuid):
        """
        Retrieve host information for a specified host instance.
        """
        host = self.get_object(host_uuid)
        serializer = HostSerializer(host, context = {'request': request})
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
        serializer = HostSerializer(host, data = request.data,
                                    context = {'request': request},
                                    partial = True)
        if serializer.is_valid():
            try:
                serializer.update(host, serializer.validated_data)
            except ValidationError as err:
                raise CustomException(str(err), status_code = status.HTTP_400_BAD_REQUEST)
            serializer = HostSerializer(host, context = {'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

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
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.DjangoModelPermissions,
    #                       permissions.IsAdminUser)
    queryset = Storage.objects.all().order_by('storage_name')
    lookup_field = 'storage_uuid'

    def exist_object(self, **kwargs):
        new_kwargs = {}
        for key in kwargs.keys():
            if key in ('storage_uuid', 'storage_name', 'storage_path'):
                if len(kwargs.get(key)) > 1:
                    return False
                else:
                    new_kwargs[key] = kwargs.get(key)[0]

        if new_kwargs:
            try:
                logger.debug("StorageList@exist_object@new_kwargs:%s" % str(new_kwargs))
                logger.debug("StorageList@exist_object@objects:%s" % str(self.queryset.get(**new_kwargs)))
                return self.queryset.get(**new_kwargs)
            except Host.DoesNotExist:
                return False

    def get(self, request, format = None):
        """
        Get all storage objects.
        """
        query_params = request.query_params
        if query_params and (query_params.get('storage_uuid') or \
                             query_params.get('storage_name') or \
                             query_params.get('storage_path')):
            if not self.exist_object(**query_params):
                return Response({
                    "status": "Failed.",
                    "status_code": status.HTTP_404_NOT_FOUND
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
        Create a storage instance.
        """
        serializer = StorageSerializer(data = request.data,
                                       context = {'request': request})
        if serializer.is_valid():
            storage = serializer.create(serializer.validated_data)
            serializer = StorageSerializer(storage, context = {'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class StorageDetail(generics.GenericAPIView):
    """
    Retrieve, update a storage instance.
    """
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.IsAdminUser)
    serializer_class = StorageSerializer
    queryset = Storage.objects
    lookup_field = 'storage_uuid'
    def get_object(self, storage_uuid):
        try:
            return self.queryset.get(storage_uuid = storage_uuid)
        except Storage.DoesNotExist:
            raise CustomException("Not Found the Storage Instance.", status_code = status.HTTP_404_NOT_FOUND)

    def get(self, request, host_uuid):
        """
        Retrieve storage information for a specified storage instance.
        """
        storage = self.get_object(storage_uuid)
        serializer = StorageSerializer(storage, context = {'request': request})
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
        serializer = StorageSerializer(storage, data = request.data,
                                       context = {'request': request},
                                       partial = True)
        if serializer.is_valid():
            serializer.update(storage, serializer.validated_data)
            serializer = StorageSerializer(storage, context = {'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
