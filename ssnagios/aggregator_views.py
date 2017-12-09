import logging
from django.http import Http404
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from ssnagios.permissions import IsOwnerOrAdmin
from ssnagios.exceptions import CustomException
from ssnagios.serializers import (AggregatorSerializer)
from ssnagios.models import get_data

logger = logging.getLogger(__name__)

class AggregatorGroupList(generics.GenericAPIView):
    """
    List all aggregators within a hostgroup.
    """
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.DjangoModelPermissions,
    #                       permissions.IsAdminUser)

    def get(self, request, hostgroup_id):
        """
        Get Aggregator List of HostGroup.
        """
        endpoint = 'hostgroup/%s/aggregators' % hostgroup_id
        status_code, json_response = get_data(endpoint)
        return Response({
            "status": "Success" if status_code == 200 else "Failed",
            "status_code": status_code,
            "data": json_response
        })


class AggregatorList(generics.GenericAPIView):
    """

    """
    serializer_class = AggregatorSerializer
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.DjangoModelPermissions,
    #                       permissions.IsAdminUser)

    def post(self, request):
        """
        Create a aggregator instance.
        """
        endpoint = 'aggregator'
        serializer = AggregatorSerializer(data = request.data,
                                         context = {'request': request})
        if serializer.is_valid():
            validated_data = serializer.validated_data
            logger.debug(validated_data)
            status_code, json_response = get_data(endpoint,
                                                  json_data = validated_data,
                                                  method = 'POST')
            logger.debug(status_code, json_response)
            return Response({
                "status": "Success" if status_code == 201 else "Failed",
                "status_code": status_code,
                "data": json_response
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """
        Update a aggregator
        """
        endpoint = 'aggregator'
        serializer = AggregatorSerializer(data = request.data,
                                         context = {'request': request})
        if serializer.is_valid():
            validated_data = serializer.validated_data
            status_code, json_response = get_data(endpoint,
                                                  json_data = validated_data,
                                                  method = 'PUT')
            return Response({
                "status": "Success" if status_code == 200 else "Failed",
                "status_code": status_code,
                "data": json_response
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class AggregatorDetail(generics.GenericAPIView):
    """

    """
    serializer_class = AggregatorSerializer
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.DjangoModelPermissions,
    #                       permissions.IsAdminUser)

    def get(self, request, aggregator_id):
        """
        Get a aggregator instance.
        """
        endpoint = 'aggregator/%s' % aggregator_id
        status_code, json_response = get_data(endpoint,
                                              method = 'GET')
        return Response({
            "status": "Success" if status_code == 200 else "Failed",
            "status_code": status_code,
            "data": json_response
        })

    def delete(self, request, aggregator_id):
        """
        delete a aggregator
        """
        endpoint = 'aggregator/%s' % aggregator_id
        status_code, json_response = get_data(endpoint,
                                              method = 'DELETE')
        return Response({
            "status": "Success" if status_code == 200 else "Failed",
            "status_code": status_code,
            "data": json_response
        })
