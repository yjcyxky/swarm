import logging
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from sshostmgt.models import (IPMI, Host, Tag)
from sshostmgt.pagination import CustomPagination
from sshostmgt.permissions import IsOwnerOrAdmin
from sshostmgt.exceptions import CustomException
from sshostmgt.serializers import (IPMISerializer, TagSerializer, HostSerializer)

logger = logging.getLogger(__name__)

class IPMIList(APIView):
    """
    List all ipmi objects, or create a new ipmi.
    """
    pagination_class = CustomPagination
    serializer_class = IPMISerializer
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.DjangoModelPermissions,
    #                       permissions.IsAdminUser)
    queryset = IPMI.objects.all().order_by('ipmi_addr')

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
            serializer.save()
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "user_info": serializer.data
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
                serializer.update(ipmi, serializer.validated_data)
                return Response({
                    "status": "Updated Success",
                    "status_code": status.HTTP_200_OK,
                    "user_info": serializer.data
               })
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        except IPMI.DoesNotExist:
            raise Http404


class IPMIDetail(APIView):
    """
    Retrieve, update a ipmi instance.
    """
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.IsAdminUser)
    queryset = IPMI.objects
    def get_object(self, pk):
        try:
            return self.queryset.get(pk = pk)
        except IPMI.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """
        Retrieve ipmi information for a specified ipmi instance.
        """
        ipmi = self.get_object(pk)
        serializer = IPMISerializer(ipmi, context = {'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "user_info": serializer.data
       })
