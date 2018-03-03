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
from report_engine.models import (ReportNode, SectionNode)
from report_engine.serializers import (ReportNodeSerializer,
                                       SectionNodeSerializer)
from report_engine.permissions import (IsOwnerOrAdmin,
                                       CustomDjangoModelPermissions)
from report_engine.pagination import CustomPagination
from report_engine.exceptions import CustomException

logger = logging.getLogger(__name__)


class ReportList(generics.GenericAPIView):
    """
    List all reports information, or create a new report infomation instance.
    """
    pagination_class = CustomPagination
    serializer_class = ReportNodeSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwnerOrAdmin)
    queryset = ReportNode.objects.all().order_by("created_time")
    lookup_field = 'report_uuid'

    def get(self, request, format=None):
        """
        Get all reports.
        """
        queryset = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a report instance.
        """
        serializer = ReportNodeSerializer(data=request.data,
                                          context={'request': request})
        if serializer.is_valid():
            report = serializer.create(serializer.validated_data)
            serializer = ReportNodeSerializer(report,
                                              context={'request': request})
            return Response({
                "status": "Created Success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class ReportDetail(generics.GenericAPIView):
    """
    Retrieve, update a report information instance.
    """
    permission_classes = (permissions.IsAuthenticated,
                          CustomDjangoModelPermissions,
                          IsOwnerOrAdmin,)
    serializer_class = ReportNodeSerializer
    queryset = ReportNode.objects
    lookup_field = 'report_uuid'

    def get_object(self, report_uuid):
        try:
            obj = self.queryset.get(report_uuid=report_uuid)
            # self.check_object_permissions(self.request, obj)
            return obj
        except ReportNode.DoesNotExist:
            raise CustomException("Not Found the Report.",
                                  status_code=status.HTTP_404_NOT_FOUND)

    def get(self, request, report_uuid):
        """
        Retrieve report information for a specified report instance.
        """
        report = self.get_object(report_uuid)
        serializer = ReportNodeSerializer(report, context={'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        })

    def put(self, request, report_uuid):
        """
        Modify report information.
        """
        report = self.get_object(report_uuid)
        serializer = ReportNodeSerializer(report, data=request.data,
                                          context={'request': request},
                                          partial=True)
        if serializer.is_valid():
            report = serializer.update(report, serializer.validated_data)
            serializer = ReportNodeSerializer(report,
                                              context={'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, report_uuid):
        """
        Delete report instance and all version reports.
        """
        try:
            report = self.get_object(report_uuid)
            # Delete All Version items
            version_set = report.version_set.all()
            for version in version_set:
                logger.debug("Delete Version Instance %s" % version)
                version.delete()
            # Clear Relationships
            report.version_set.clear()

            # Delete Report Instance
            # The root_node_set will delete automatically for the CASCADE flag.
            logger.debug("Delete Report Instance %s" % report)
            report.delete()
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


class RootNodeList(generics.GenericAPIView):
    """
    List all version reports, or create a new report.
    """
    pagination_class = CustomPagination
    serializer_class = SectionNodeSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsOwnerOrAdmin)
    queryset = SectionNode.objects.all().order_by("created_time")
    lookup_field = 'section_uuid'

    def get_queryset(self, filters=None):
        try:
            if filters:
                return self.queryset.filter(**filters)
        except SectionNode.DoesNotExist:
            raise CustomException("Not Found the RootNode Instance.",
                                  status_code=status.HTTP_404_NOT_FOUND)

    def get(self, request, report_uuid, format=None):
        """
        Get all version reports.
        """
        filters = {
            'report': report_uuid,
            'node_type': 'ROOT'
        }
        queryset = self.paginate_queryset(self.get_queryset(filters))
        serializer = self.get_serializer(queryset, many=True,
                                         context={'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request, report_uuid):
        """
        Create a new version of specified report instance.
        """
        serializer = SectionNodeSerializer(data=request.data,
                                           context={'request': request})
        if serializer.is_valid():
            if serializer.validated_data.get('node_type', '').upper() \
               != 'ROOT':
                raise CustomException("The node_type of the first section_node"
                                      " must be ROOT.",
                                      status_code=status.HTTP_400_BAD_REQUEST)
            report = serializer.create(serializer.validated_data)
            serializer = SectionNodeSerializer(report,
                                               context={'request': request})
            return Response({
                "status": "Created Success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RootNodeDetail(generics.GenericAPIView):
    """
    Retrieve, update a report instance.
    """
    # permission_classes = (permissions.IsAuthenticated,
    #                       CustomDjangoModelPermissions,
    #                       IsOwnerOrAdmin,)
    serializer_class = ReportNodeSerializer
    queryset = SectionNode.objects
    lookup_field = 'report_uuid'

    def get_object(self, report_uuid, version_uuid):
        try:
            obj = self.queryset.get(report=report_uuid,
                                    section_uuid=version_uuid)
            # self.check_object_permissions(self.request, obj)
            return obj
        except SectionNode.DoesNotExist:
            raise CustomException("Not Found the Report.",
                                  status_code=status.HTTP_404_NOT_FOUND)

    def get(self, request, report_uuid, version_uuid):
        """
        Retrieve report information for a specified report instance.
        """
        report = self.get_object(report_uuid, version_uuid)
        serializer = SectionNodeSerializer(report,
                                           context={'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        })

    def put(self, request, report_uuid, version_uuid):
        """
        Modify report information.
        """
        report = self.get_object(report_uuid, version_uuid)
        serializer = SectionNodeSerializer(report, data=request.data,
                                           context={'request': request},
                                           partial=True)
        if serializer.is_valid():
            report = serializer.update(report, serializer.validated_data)
            serializer = SectionNodeSerializer(report,
                                               context={'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, report_uuid, version_uuid):
        """
        Delete report instance.
        """
        pass
