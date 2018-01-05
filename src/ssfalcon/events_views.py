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
from ssfalcon.permissions import IsOwnerOrAdmin
from ssfalcon.exceptions import CustomException
from ssfalcon.serializers import (AggregatorSerializer, EventSerializer)
from ssfalcon.models import get_data

logger = logging.getLogger(__name__)

class EventCaseList(generics.GenericAPIView):
    """
    List all event cases.
    """
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.DjangoModelPermissions,
    #                       permissions.IsAdminUser)
    serializer_class = EventSerializer

    def get(self, request):
        """
        Get event cases.
        """
        endpoint = 'alarm/eventcases'
        status_code, json_response = get_data(endpoint,
                                              params = request.query_params)
        return Response({
            "status": "Success" if status_code == 200 else "Failed",
            "status_code": status_code,
            "data": json_response
        })

    def post(self, request):
        """
        Create an event case.
        """
        endpoint = 'alarm/eventcases'
        serializer = EventSerializer(data = request.data,
                                     context = {'request': request})
        if serializer.is_valid():
            validated_data = serializer.validated_data
            status_code, json_response = get_data(endpoint,
                                                  json_data = validated_data,
                                                  method = 'POST')
            return Response({
                "status": "Success" if status_code == 200 else "Failed",
                "status_code": status_code,
                "data": json_response
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class EventNoteList(generics.GenericAPIView):
    """
    List all event notes.
    """
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.DjangoModelPermissions,
    #                       permissions.IsAdminUser)
    serializer_class = EventSerializer

    def get(self, request):
        """
        Get event notes.
        """
        endpoint = 'alarm/event_note'
        status_code, json_response = get_data(endpoint,
                                              params = request.query_params)
        return Response({
            "status": "Success" if status_code == 200 else "Failed",
            "status_code": status_code,
            "data": json_response
        })

    def post(self, request):
        """
        Create an event note.
        """
        endpoint = 'alarm/event_note'
        serializer = EventSerializer(data = request.data,
                                     context = {'request': request})
        if serializer.is_valid():
            validated_data = serializer.validated_data
            status_code, json_response = get_data(endpoint,
                                                  json_data = validated_data,
                                                  method = 'POST')
            return Response({
                "status": "Success" if status_code == 200 else "Failed",
                "status_code": status_code,
                "data": json_response
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class EventList(generics.GenericAPIView):
    """
    List all events.
    """
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.DjangoModelPermissions,
    #                       permissions.IsAdminUser)
    serializer_class = EventSerializer

    def post(self, request):
        """
        Create an event.
        """
        endpoint = 'alarm/events'
        serializer = EventSerializer(data = request.data,
                                     context = {'request': request})
        if serializer.is_valid():
            validated_data = serializer.validated_data
            status_code, json_response = get_data(endpoint,
                                                  form_data = validated_data,
                                                  method = 'POST')
            return Response({
                "status": "Success" if status_code == 200 else "Failed",
                "status_code": status_code,
                "data": json_response
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
