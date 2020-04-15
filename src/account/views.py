# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import logging
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from account.serializers import (UserSerializer)
from account.pagination import CustomPagination

logger = logging.getLogger(__name__)


class UserList(generics.GenericAPIView):
    """
    List all users, or create a new user.
    """
    pagination_class = CustomPagination
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by("username")
    lookup_field = 'id'
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self, filters = None):
        if filters:
            return User.objects.all().filter(**filters)
        else:
            return User.objects.all()

    def get(self, request, format=None):
        """
        Get all users.
        """
        query_params = request.query_params
        filters = {}

        username = query_params.get('username')
        if username:
            filters.update({'username': username})

        is_staff = query_params.get('is_staff')
        if is_staff:
            filters.update({'is_staff': True if is_staff == 'true' else False})

        is_active = query_params.get('is_active')
        if is_active:
            filters.update({'is_staff': True if is_active == 'true' else False})

        queryset = self.paginate_queryset(self.get_queryset(filters))
        serializer = self.get_serializer(queryset, many = True,
                                         context = {'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a user instance.
        """
        serializer = UserSerializer(data=request.data,
                                    context={'request': request})
        if serializer.is_valid():
            user = serializer.create(serializer.validated_data)
            serializer = UserSerializer(user, context={'request': request})
            return Response({
                "status": "Created Success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response({
            'status': 'Bad Request',
            'message': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(APIView):
    """
    Retrieve, update a user instance.
    """
    queryset = User.objects
    lookup_field = 'id'

    def get_object(self, pk):
        filter = {
            'pk': pk
        }

        obj = get_object_or_404(self.queryset, **filter)
        return obj

    def get(self, request, pk):
        """
        Retrieve account information for a specified user.
        """
        user = self.get_object(pk)
        serializer = UserSerializer(user, context={'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        })

    def put(self, request, pk):
        """
        Modify password for the user.
        """
        # 普通用户无法access PUT方法
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data,
                                    context={'request': request},
                                    partial=True)
        if serializer.is_valid():
            user = serializer.update(user, serializer.validated_data)
            serializer = UserSerializer(user, context={'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response({
            'status': 'Bad Request',
            'message': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete the user.
        """
        try:
            user = self.get_object(pk)
            user.delete()
            return Response({
                "status_code": status.HTTP_204_NO_CONTENT,
                "status": "No Content.",
                "data": []
            })
        except:
            return Response({
                "status": "Not Found.",
                "status_code": status.HTTP_404_NOT_FOUND,
                "data": []
            })


@api_view(['GET'])
def current_user(request):
    """
    Retrieve account information for current user.
    """
    user = request.user
    serializer = UserSerializer(user, context={'request': request})
    return Response({
        "status": "Success",
        "status_code": status.HTTP_200_OK,
        "data": serializer.data
    })
