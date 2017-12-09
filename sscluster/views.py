import logging
from django.http import Http404
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from sscluster.models import (Cluster, JobLog)
from sscluster.pagination import CustomPagination
from sscluster.permissions import IsOwnerOrAdmin
from sscluster.exceptions import CustomException
from sscluster.serializers import (ClusterSerializer, JobLogSerializer)

logger = logging.getLogger(__name__)

class ClusterList(generics.GenericAPIView):
    """
    List all cluster objects, or create a cluster instance.
    """
    pagination_class = CustomPagination
    serializer_class = ClusterSerializer
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.DjangoModelPermissions,
    #                       permissions.IsAdminUser)
    queryset = Cluster.objects.all().order_by('cluster_name')
    lookup_field = 'cluster_uuid'

    def exist_object(self, **kwargs):
        new_kwargs = {}
        for key in kwargs.keys():
            if key in ('cluster_uuid', 'cluster_name'):
                if len(kwargs.get(key)) > 1:
                    return False
                else:
                    new_kwargs[key] = kwargs.get(key)[0]

        if new_kwargs:
            try:
                logger.debug("ClusterList@exist_object@new_kwargs:%s" % str(new_kwargs))
                logger.debug("ClusterList@exist_object@objects:%s" % str(self.queryset.get(**new_kwargs)))
                return self.queryset.get(**new_kwargs)
            except Cluster.DoesNotExist:
                return False

    def get(self, request, format = None):
        """
        Get all cluster objects.
        """
        query_params = request.query_params
        if query_params and (query_params.get('cluster_uuid') or \
                             query_params.get('cluster_name')):
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
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.IsAdminUser)
    serializer_class = ClusterSerializer
    queryset = Cluster.objects
    lookup_field = 'cluster_uuid'

    def get_object(self, cluster_uuid):
        try:
            return self.queryset.get(cluster_uuid = cluster_uuid)
        except Cluster.DoesNotExist:
            # raise Http404
            return Response({
                "status": "Not Found.",
                "status_code": status.HTTP_404_NOT_FOUND,
                "data": []
            })

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
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.DjangoModelPermissions,
    #                       permissions.IsAdminUser)
    queryset = JobLog.objects.all().order_by('job_id')
    lookup_field = 'job_uuid'

    def get(self, request, format = None):
        """
        Get all joblog objects.
        """
        queryset = self.paginate_queryset(self.get_queryset())
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
    # permission_classes = (permissions.IsAuthenticated,
    #                       permissions.IsAdminUser)
    serializer_class = JobLogSerializer
    queryset = JobLog.objects
    lookup_field = 'job_uuid'

    def get_object(self, job_uuid = None, job_id = None):
        try:
            if job_uuid:
                return self.queryset.get(job_uuid = job_uuid)
            if job_id:
                return self.queryset.get(job_id = job_id)
        except JobLog.DoesNotExist:
            # raise Http404
            return Response({
                "status": "Not Found.",
                "status_code": status.HTTP_404_NOT_FOUND,
                "data": []
            })

    def get(self, request, job_uuid = None, job_id = None):
        """
        Retrieve joblog information for a specified joblog instance.
        """
        joblog = self.get_object(job_uuid = job_uuid, job_id = job_id)
        serializer = JobLogSerializer(joblog, context = {'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        })

    def put(self, request, job_uuid = None, job_id = None):
        """
        Modify joblog information.
        """
        joblog = self.get_object(job_uuid = job_uuid, job_id = job_id)
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
