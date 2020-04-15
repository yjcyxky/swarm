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
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.db.models import (Count, Sum)
from django_filters.rest_framework import DjangoFilterBackend
from sscluster.models import (Cluster, JobLog, ToDoList)
from sscluster.pagination import CustomPagination
from sscluster.exceptions import CustomException
from sscluster.serializers import (ClusterSerializer, JobLogSerializer,
                                   JobLogCountSerializer, ToDoListSerializer)
from django.db import connection

logger = logging.getLogger(__name__)

class ClusterList(generics.GenericAPIView):
    """
    List all cluster objects, or create a cluster instance.
    """
    pagination_class = CustomPagination
    serializer_class = ClusterSerializer
    queryset = Cluster.objects.all().order_by('cluster_name')
    lookup_field = 'cluster_uuid'
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self, filters = None):
        if filters:
            return Cluster.objects.all().filter(**filters)
        else:
            return Cluster.objects.all()

    def get(self, request, format = None):
        """
        Get all cluster objects.
        """
        query_params = request.query_params
        filters = {}

        cluster_name = query_params.get('cluster_name')
        if cluster_name:
            filters.update({'cluster_name': cluster_name})

        queryset = self.paginate_queryset(self.get_queryset(filters))
        serializer = self.get_serializer(queryset, many = True,
                                         context = {'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a cluster instance.
        """
        serializer = ClusterSerializer(data = request.data,
                                       context = {'request': request})
        if serializer.is_valid():
            cluster = serializer.create(serializer.validated_data)
            serializer = ClusterSerializer(cluster, context = {'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class ClusterDetail(generics.GenericAPIView):
    """
    Retrieve, update a cluster instance.
    """
    serializer_class = ClusterSerializer
    queryset = Cluster.objects
    lookup_field = 'cluster_uuid'

    def get_object(self, cluster_uuid):
        try:
            return self.queryset.get(cluster_uuid = cluster_uuid)
        except Cluster.DoesNotExist:
            raise CustomException("Not Found the Cluster.", status_code = status.HTTP_404_NOT_FOUND)

    def get(self, request, cluster_uuid):
        """
        Retrieve cluster information for a specified cluster instance.
        """
        cluster = self.get_object(cluster_uuid)
        serializer = ClusterSerializer(cluster, context = {'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
       })

    def put(self, request, cluster_uuid):
        """
        Modify cluster information.
        """
        cluster = self.get_object(cluster_uuid)
        serializer = ClusterSerializer(cluster, data = request.data,
                                       context = {'request': request},
                                       partial = True)
        if serializer.is_valid():
            cluster = serializer.update(cluster, serializer.validated_data)
            serializer = ClusterSerializer(cluster, context = {'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class JobLogList(generics.GenericAPIView):
    """
    List all joblog objects, or create a new joblog.
    """
    pagination_class = CustomPagination
    serializer_class = JobLogSerializer
    queryset = JobLog.objects.all().order_by('-jobid')
    lookup_field = 'job_uuid'
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self, filters = None):
        if filters:
            return JobLog.objects.all().filter(**filters)
        else:
            return JobLog.objects.all()

    def get(self, request, format = None):
        """
        Get all joblog objects.
        """
        query_params = request.query_params
        filters = {}

        try:
            exit_status = query_params.get('exit_status')
            if exit_status:
                filters.update({'exit_status': int(exit_status)})

            if query_params.get('start'):
                filters.update({
                    'start__gt': query_params.get('start', '2012-12-12 08:00:00')
                })

            if query_params.get('end'):
                filters.update({
                    'end__lt': query_params.get('end', '2100-12-12 08:00:00'),
                })

        except ValueError:
            raise CustomException("Bad Request.", status_code = status.HTTP_400_BAD_REQUEST)

        username = query_params.get('user')
        if username:
            filters.update({'user__username': username})

        queryset = self.paginate_queryset(self.get_queryset(filters))
        serializer = self.get_serializer(queryset, many = True,
                                         context = {'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a joblog instance.
        """
        serializer = JobLogSerializer(data = request.data,
                                      context = {'request': request})
        if serializer.is_valid():
            joblog = serializer.create(serializer.validated_data)
            serializer = JobLogSerializer(joblog, context = {'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class JobLogDetail(generics.GenericAPIView):
    """
    Retrieve, update a joblog instance.
    """
    serializer_class = JobLogSerializer
    queryset = JobLog.objects
    lookup_field = 'job_uuid'

    def get_object(self, job_uuid = None, jobid = None):
        try:
            if job_uuid:
                return self.queryset.get(job_uuid = job_uuid)
            if jobid:
                return self.queryset.get(jobid = jobid)
        except JobLog.DoesNotExist:
            raise CustomException("Not Found the Job Log Instance.", status_code = status.HTTP_404_NOT_FOUND)

    def get(self, request, job_uuid = None, jobid = None):
        """
        Retrieve joblog information for a specified joblog instance.
        """
        joblog = self.get_object(job_uuid = job_uuid, jobid = jobid)
        serializer = JobLogSerializer(joblog, context = {'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        })

    def put(self, request, job_uuid = None, jobid = None):
        """
        Modify joblog information.
        """
        joblog = self.get_object(job_uuid = job_uuid, jobid = jobid)
        serializer = JobLogSerializer(joblog, data = request.data,
                                      context = {'request': request},
                                      partial = True)
        if serializer.is_valid():
            joblog = serializer.update(joblog, serializer.validated_data)
            serializer = JobLogSerializer(joblog, context = {'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class JobLogCount(generics.GenericAPIView):
    """
    Get count of JobLog Records.
    """
    serializer_class = JobLogCountSerializer
    pagination_class = CustomPagination
    queryset = User.objects
    lookup_field = 'job_uuid'

    def get_queryset(self, filters = None, select_by = 'year'):
        selected_values = {
            'year': ('joblog__owner', 'year', 'joblog__cluster_uuid'),
            'month': ('joblog__owner', 'month', 'joblog__cluster_uuid'),
            'day': ('joblog__owner', 'day', 'joblog__cluster_uuid'),
        }
        selections = {
            'year': {
                'year': connection.ops.date_trunc_sql('year', 'start')
            },
            'month': {
                'month': connection.ops.date_trunc_sql('month', 'start')
            },
            'day': {
                'day': connection.ops.date_trunc_sql('day', 'start')
            },
        }
        logger.debug('JobLogCount@get_count@selected_values@%s' % str(selected_values.get(select_by)))
        try:
            if filters:
                return self.queryset.extra(select=selections.get(select_by))\
                                    .filter(**filters)\
                                    .values(*selected_values.get(select_by))\
                                    .annotate(records_count = Count('joblog'),
                                              used_cput = Sum('joblog__resources_used_cput'),
                                              used_mem = Sum('joblog__resources_used_mem'),
                                              used_vmem = Sum('joblog__resources_used_vmem'))\
                                    .order_by('joblog__owner')
            else:
                return self.queryset.extra(select=selections.get(select_by))\
                                    .values(*selected_values.get(select_by))\
                                    .annotate(records_count = Count('joblog'),
                                              used_cput = Sum('joblog__resources_used_cput'),
                                              used_mem = Sum('joblog__resources_used_mem'),
                                              used_vmem = Sum('joblog__resources_used_vmem'))\
                                    .order_by('joblog__owner')
        except User.DoesNotExist:
            raise CustomException("Not Found the JobLog.", status_code = status.HTTP_404_NOT_FOUND)

    def get(self, request):
        """
        Get Count.
        """
        query_params = request.query_params
        # 防止用户输入引号空格等
        select_by = query_params.get('select_by', 'year').strip(' \'"')
        start = query_params.get('start')
        end = query_params.get('end')
        try:
            exit_status = int(query_params.get('exit_status', 0))
        except ValueError:
            raise CustomException("Bad Request.", status_code = status.HTTP_400_BAD_REQUEST)

        logger.debug("sscluster@JobLogCount@%s-%s" % (query_params, select_by))

        filters = {}
        if exit_status:
            filters.update({
                'joblog__exit_status': exit_status
            })
        if start:
            filters.update({
                'joblog__start__gt': start
            })
        if end:
            filters.update({
                'joblog__end__lt': end,
            })

        queryset = self.paginate_queryset(self.get_queryset(filters, select_by))
        print(self.get_queryset({}, select_by))
        serializer = self.get_serializer(queryset, many = True,
                                         context = {'request': request})
        return self.get_paginated_response(serializer.data)

class ToDoListList(generics.GenericAPIView):
    """
    List all ToDoList objects, or create a ToDoList instance.
    """
    pagination_class = CustomPagination
    serializer_class = ToDoListSerializer
    queryset = ToDoList.objects.all().order_by('item_name')
    lookup_field = 'id'
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self, filters = None):
        if filters:
            return ToDoList.objects.all().filter(**filters)
        else:
            return ToDoList.objects.all()

    def get(self, request, format = None):
        """
        Get all ToDoList objects.
        """
        query_params = request.query_params
        filters = {'user': request.user}

        queryset = self.paginate_queryset(self.get_queryset(filters))
        serializer = self.get_serializer(queryset, many = True,
                                            context = {'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a ToDoList instance.
        """
        serializer = ToDoListSerializer(data = request.data,
                                         context = {'request': request})
        if serializer.is_valid():
            todolist = serializer.create(serializer.validated_data)
            serializer = ToDoListSerializer(todolist, context = {'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class ToDoListDetail(generics.GenericAPIView):
    """
    Retrieve, update a ToDoList instance.
    """
    serializer_class = ToDoListSerializer
    queryset = ToDoList.objects
    lookup_field = 'id'

    def get_object(self, pk):
        try:
            return self.queryset.get(pk = pk)
        except ToDoList.DoesNotExist:
            raise CustomException("Not Found the ToDoList Instance.", status_code = status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        """
        Retrieve the todolist information for a specified todolist instance.
        """
        todolist_item = self.get_object(pk)
        serializer = ToDoListSerializer(todolist_item, context = {'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
       })

    def put(self, request, pk):
        """
        Modify a todolist instance information.
        """
        todolist_item = self.get_object(pk)
        serializer = ToDoListSerializer(todolist_item, data = request.data,
                                         context = {'request': request},
                                         partial = True)
        if serializer.is_valid():
            todolist_item = serializer.update(todolist_item, serializer.validated_data)
            serializer = ToDoListSerializer(todolist_item, context = {'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Delete a todolist instance.
        """
        todolist_item = self.get_object(pk)
        todolist_item.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)
