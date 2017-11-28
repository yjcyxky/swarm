import logging
from django.http import Http404
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from sshostmgt.models import (IPMI, Host, Tag)
from sshostmgt.pagination import CustomPagination
from sshostmgt.permissions import IsOwnerOrAdmin
from sshostmgt.exceptions import CustomException
from sshostmgt.serializers import (IPMISerializer, TagSerializer, HostSerializer)

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

    def get(self, request, format = None):
        """
        Get all ipmi objects.
        """
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
                "ipmi_info": serializer.data
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
                    "ipmi_info": serializer.data
               })
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        except IPMI.DoesNotExist:
            raise Http404


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
            raise Http404

    def get(self, request, ipmi_uuid):
        """
        Retrieve ipmi information for a specified ipmi instance.
        """
        ipmi = self.get_object(ipmi_uuid)
        serializer = IPMISerializer(ipmi, context = {'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "ipmi_info": serializer.data
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
                "ipmi_info": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


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
                "tag_info": serializer.data
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
            raise Http404

    def get(self, request, tag_uuid):
        """
        Retrieve tag information for a specified tag instance.
        """
        tag = self.get_object(tag_uuid)
        serializer = TagSerializer(tag, context = {'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "tag_info": serializer.data
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
                "tag_info": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class HostList(generics.GenericAPIView):
    """
    List all host objects, or create a new host.
    """
    pagination_class = CustomPagination
    serializer_class = HostSerializer
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.DjangoModelPermissions,
    #                       permissions.IsAdminUser)
    queryset = Host.objects.all().order_by('hostname')
    lookup_field = 'host_uuid'

    def get(self, request, format = None):
        """
        Get all host objects.
        """
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
                "host_info": serializer.data
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
            raise Http404

    def get(self, request, host_uuid):
        """
        Retrieve host information for a specified host instance.
        """
        host = self.get_object(host_uuid)
        serializer = HostSerializer(host, context = {'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "host_info": serializer.data
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
            serializer.update(host, serializer.validated_data)
            serializer = HostSerializer(host, context = {'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "host_info": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
