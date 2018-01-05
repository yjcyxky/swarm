# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import logging
import uuid
from django.http import Http404
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.db.models import (Count, Sum)
import django_filters.rest_framework
from rest_framework.decorators import (api_view, permission_classes)
from ssadvisor.models import (Patient, Report, UserReport, File, UserFile,
                              Task, TaskPool, UserTask, AdvisorSetting)
from ssadvisor.pagination import CustomPagination
from ssadvisor.permissions import IsOwnerOrAdmin
from ssadvisor.exceptions import (CustomException, AdvisorWrongSetting)
from ssadvisor.serializers import (PatientSerializer, ReportSerializer,
                                   UserReportSerializer, FileSerializer,
                                   UserFileSerializer, TaskSerializer,
                                   UserTaskSerializer, SettingSerializer,
                                   TaskPoolSerializer,)
from ssadvisor.utils import get_settings
from sscobweb.models import CobwebSetting
from ssadvisor.tasks import submit_job, update_jobstatus
from ssadvisor.permissions import (IsOwnerOrAdmin, CustomDjangoModelPermissions)

logger = logging.getLogger(__name__)

class PatientList(generics.GenericAPIView):
    """
    List all patient objects, or create a patient instance.
    """
    pagination_class = CustomPagination
    serializer_class = PatientSerializer
    permission_classes = (permissions.IsAuthenticated,
                          CustomDjangoModelPermissions,
                          permissions.IsAdminUser)
    queryset = Patient.objects.all().order_by('case_id')
    lookup_field = 'patient_uuid'

    def exist_object(self, **kwargs):
        new_kwargs = {}
        for key in kwargs.keys():
            if key in ('patient_uuid'):
                if len(kwargs.get(key)) > 1:
                    return False
                else:
                    new_kwargs[key] = kwargs.get(key)[0]

        if new_kwargs:
            try:
                logger.debug("PatientList@exist_object@new_kwargs:%s" % str(new_kwargs))
                logger.debug("PatientList@exist_object@objects:%s" % str(self.queryset.get(**new_kwargs)))
                return self.queryset.get(**new_kwargs)
            except Patient.DoesNotExist:
                return False

    def get_queryset(self, filters = None):
        try:
            if filters:
                return Patient.objects.all().filter(**filters).order_by('-created_time')
            else:
                return Patient.objects.all().order_by('-created_time')
        except Patient.DoesNotExist:
            raise CustomException("Not Found the Patient.", status_code = status.HTTP_404_NOT_FOUND)

    def get(self, request, format = None):
        """
        Get all patient objects.
        """
        query_params = request.query_params
        filters = {}
        if query_params.get('created_time'):
            filters.update({
                'created_time__gt': query_params.get('start', '2012-12-12 08:00:00'),
            })
        if query_params.get('checked_time'):
            filters.update({
                'checked_time__lt': query_params.get('end', '2100-12-12 08:00:00')
            })
        if query_params.get('checked'):
            filters.update({
                'checked': True if query_params.get('checked').upper() == 'TRUE' else False
            })

        if query_params and query_params.get('patient_uuid'):
            if not self.exist_object(**query_params):
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
            queryset = self.paginate_queryset(self.get_queryset(filters))
            serializer = self.get_serializer(queryset, many = True,
                                             context = {'request': request})
            return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a patient instance.
        """
        serializer = PatientSerializer(data = request.data,
                                       context = {'request': request})
        if serializer.is_valid():
            patient = serializer.create(serializer.validated_data)
            serializer = PatientSerializer(patient, context = {'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class PatientDetail(generics.GenericAPIView):
    """
    Retrieve, update a patient instance.
    """
    permission_classes = (permissions.IsAuthenticated,
                          CustomDjangoModelPermissions,
                          IsOwnerOrAdmin,)
    serializer_class = PatientSerializer
    queryset = Patient.objects
    lookup_field = 'patient_uuid'

    def get_object(self, patient_uuid):
        try:
            obj = self.queryset.get(patient_uuid = patient_uuid)
            self.check_object_permissions(self.request, obj)
            return obj
        except Patient.DoesNotExist:
            raise CustomException("Not Found the Cluster.", status_code = status.HTTP_404_NOT_FOUND)

    def get(self, request, patient_uuid):
        """
        Retrieve patient information for a specified patient instance.
        """
        patient = self.get_object(patient_uuid)
        serializer = PatientSerializer(patient, context = {'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
       })

    def put(self, request, patient_uuid):
        """
        Modify patient information.
        """
        patient = self.get_object(patient_uuid)
        serializer = PatientSerializer(patient, data = request.data,
                                       context = {'request': request},
                                       partial = True)
        if serializer.is_valid():
            patient = serializer.update(patient, serializer.validated_data)
            serializer = PatientSerializer(cluster, context = {'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class ReportList(generics.GenericAPIView):
    """
    List all report objects, or create a new report.
    """
    pagination_class = CustomPagination
    serializer_class = ReportSerializer
    permission_classes = (permissions.IsAuthenticated,
                          CustomDjangoModelPermissions,
                          permissions.IsAdminUser)
    queryset = Report.objects.all().order_by('created_time')
    lookup_field = 'report_uuid'
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    def exist_object(self, **kwargs):
        new_kwargs = {}
        for key in kwargs.keys():
            if key in ('report_uuid', 'report_name'):
                if len(kwargs.get(key)) > 1:
                    return False
                else:
                    new_kwargs[key] = kwargs.get(key)[0]

        if new_kwargs:
            try:
                logger.debug("ReportList@exist_object@new_kwargs:%s" % str(new_kwargs))
                logger.debug("ReportList@exist_object@objects:%s" % str(self.queryset.get(**new_kwargs)))
                return self.queryset.get(**new_kwargs)
            except Report.DoesNotExist:
                return False

    def get_queryset(self, filters = None):
        try:
            if filters:
                return Report.objects.all().filter(**filters).order_by('-created_time')
            else:
                return Report.objects.all().order_by('-created_time')
        except Report.DoesNotExist:
            raise CustomException("Not Found the JobLog.", status_code = status.HTTP_404_NOT_FOUND)

    def get(self, request, format = None):
        """
        Get all report objects.
        """
        query_params = request.query_params
        filters = {}
        created_time = query_params.get('created_time', '2012-12-12 08:00:00')
        checked_time = query_params.get('checked_time', '2100-12-12 08:00:00')
        checked = query_params.get('checked')
        username = query_params.get('user')
        relationship = query_params.get('relationship')
        if created_time:
            filters.update({
                'created_time__gt': created_time,
            })
        if checked_time:
            filters.update({
                'checked_time__lt': checked_time,
            })
        if checked:
            filters.update({
                'checked': True if query_params.get('checked').upper() == 'TRUE' else False
            })
        if username:
            filters.update({'user__username': username})
        if relationship:
            filters.update({'userreport__relationship': relationship})

        if query_params and (query_params.get('report_uuid') or \
                             query_params.get('report_name')):
            if not self.exist_object(**query_params):
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
            queryset = self.paginate_queryset(self.get_queryset(filters))
            serializer = self.get_serializer(queryset, many = True,
                                             context = {'request': request})
            return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a report instance.
        """
        serializer = ReportSerializer(data = request.data,
                                      context = {'request': request})
        if serializer.is_valid():
            report = serializer.create(serializer.validated_data)
            serializer = ReportSerializer(report, context = {'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class ReportDetail(generics.GenericAPIView):
    """
    Retrieve, update a report instance.
    """
    permission_classes = (permissions.IsAuthenticated,
                          CustomDjangoModelPermissions,
                          IsOwnerOrAdmin,)
    serializer_class = ReportSerializer
    queryset = Report.objects
    lookup_field = 'report_uuid'

    def get_object(self, report_uuid):
        try:
            obj = self.queryset.get(report_uuid = report_uuid)
            self.check_object_permissions(self.request, obj)
            return obj
        except Report.DoesNotExist:
            raise CustomException("Not Found the Report.", status_code = status.HTTP_404_NOT_FOUND)

    def get(self, request, report_uuid):
        """
        Retrieve report information for a specified report instance.
        """
        report = self.get_object(report_uuid)
        serializer = ReportSerializer(report, context = {'request': request})
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
        serializer = ReportSerializer(report, data = request.data,
                                      context = {'request': request},
                                      partial = True)
        if serializer.is_valid():
            report = serializer.update(report, serializer.validated_data)
            serializer = ReportSerializer(report, context = {'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class FileList(generics.GenericAPIView):
    """
    List all file objects, or create a new file.
    """
    pagination_class = CustomPagination
    serializer_class = FileSerializer
    permission_classes = (permissions.IsAuthenticated,
                          CustomDjangoModelPermissions,
                          permissions.IsAdminUser)
    queryset = File.objects.all().order_by('created_time')
    lookup_field = 'file_uuid'
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    def exist_object(self, **kwargs):
        new_kwargs = {}
        for key in kwargs.keys():
            if key in ('file_uuid', 'file_id', 'file_name', 'file_md5sum'):
                if len(kwargs.get(key)) > 1:
                    return False
                else:
                    new_kwargs[key] = kwargs.get(key)[0]

        if new_kwargs:
            try:
                logger.debug("FileList@exist_object@new_kwargs:%s" % str(new_kwargs))
                logger.debug("FileList@exist_object@objects:%s" % str(self.queryset.get(**new_kwargs)))
                return self.queryset.get(**new_kwargs)
            except File.DoesNotExist:
                return False

    def get_queryset(self, filters = None):
        try:
            if filters:
                return Report.objects.all().filter(**filters).order_by('-created_time')
            else:
                return Report.objects.all().order_by('-created_time')
        except File.DoesNotExist:
            raise CustomException("Not Found the Files.", status_code = status.HTTP_404_NOT_FOUND)

    def get(self, request, format = None):
        """
        Get all file objects.
        """
        query_params = request.query_params
        filters = {}
        created_time = query_params.get('created_time', '2012-12-12 08:00:00')
        patient_uuid = query_params.get('patient_uuid')
        username = query_params.get('username')
        relationship = query_params.get('relationship')
        if created_time:
            filters.update({
                'created_time__gt': created_time,
            })
        if patient_uuid:
            filters.update({
                'patient__patient_uuid__lt': patient_uuid,
            })
        if username:
            filters.update({'user__username': username})
        if relationship:
            filters.update({'userfile__relationship': relationship})

        if query_params and (query_params.get('file_uuid') or \
                             query_params.get('file_id') or \
                             query_params.get('file_name') or \
                             query_params.get('file_md5sum')):
            if not self.exist_object(**query_params):
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
            queryset = self.paginate_queryset(self.get_queryset(filters))
            serializer = self.get_serializer(queryset, many = True,
                                             context = {'request': request})
            return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a file instance.
        """
        serializer = FileSerializer(data = request.data,
                                    context = {'request': request})
        if serializer.is_valid():
            file = serializer.create(serializer.validated_data)
            serializer = FileSerializer(file, context = {'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class FileDetail(generics.GenericAPIView):
    """
    Retrieve, update a file instance.
    """
    permission_classes = (permissions.IsAuthenticated,
                          CustomDjangoModelPermissions,
                          IsOwnerOrAdmin,)
    serializer_class = FileSerializer
    queryset = File.objects
    lookup_field = 'file_uuid'

    def get_object(self, file_uuid):
        try:
            obj = self.queryset.get(pk = file_uuid)
            self.check_object_permissions(self.request, obj)
            return obj
        except File.DoesNotExist:
            raise CustomException("Not Found the File.", status_code = status.HTTP_404_NOT_FOUND)

    def get(self, request, file_uuid):
        """
        Retrieve file information for a specified file instance.
        """
        file = self.get_object(file_uuid)
        serializer = FileSerializer(file, context = {'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        })

    def put(self, request, file_uuid):
        """
        Modify file information.
        """
        file = self.get_object(file_uuid)
        serializer = FileSerializer(file, data = request.data,
                                    context = {'request': request},
                                    partial = True)
        if serializer.is_valid():
            file = serializer.update(file, serializer.validated_data)
            serializer = FileSerializer(file, context = {'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class TaskList(generics.GenericAPIView):
    """
    List all task objects, or create a new task.
    """
    pagination_class = CustomPagination
    permission_classes = (permissions.IsAuthenticated,
                          CustomDjangoModelPermissions,
                          permissions.IsAdminUser)
    queryset = Task.objects.all().order_by('-created_time')
    lookup_field = 'task_uuid'
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.request.query_params.get('queue'):
            return TaskPoolSerializer
        return TaskSerializer

    def exist_object(self, **kwargs):
        new_kwargs = {}
        for key in kwargs.keys():
            if key in ('task_uuid'):
                if len(kwargs.get(key)) > 1:
                    return False
                else:
                    new_kwargs[key] = kwargs.get(key)[0]

        if new_kwargs:
            try:
                logger.debug("TaskList@exist_object@new_kwargs:%s" % str(new_kwargs))
                logger.debug("TaskList@exist_object@objects:%s" % str(self.queryset.get(**new_kwargs)))
                return self.queryset.get(**new_kwargs)
            except Task.DoesNotExist:
                return False

    def get_queryset(self, filters = None):
        try:
            if filters:
                return Task.objects.all().filter(**filters).order_by('-created_time')
            else:
                return Task.objects.all().order_by('-created_time')
        except Task.DoesNotExist:
            raise CustomException("Not Found the Tasks.", status_code = status.HTTP_404_NOT_FOUND)

    def get_filters(self, query_params):
        filters = {}
        created_time = query_params.get('created_time')
        finished_time = query_params.get('finished_time')
        progress_percentage = query_params.get('progress', 0)
        patient_uuid = query_params.get('patient_uuid')
        username = query_params.get('username')
        relationship = query_params.get('relationship')

        if created_time:
            filters.update({
                'created_time__gt': created_time,
            })
        if finished_time:
            filters.update({
                'finished_time__lt': finished_time,
            })
        if patient_uuid:
            filters.update({
                'patient__patient_uuid__lt': patient_uuid,
            })
        if progress_percentage is not None:
            try:
                filters.update({
                    'progress_percentage__gte': int(progress_percentage)
                })
            except:
                raise CustomException('Wrong query_params: progress.',
                                      status_code = status.HTTP_400_BAD_REQUEST)
        if username:
            filters.update({'user__username': username})
        if relationship:
            filters.update({'usertask__relationship': relationship})
        return filters

    def check_task_pool_valid(self, max_task_num):
        try:
            if TaskPool.objects.count() < max_task_num:
                return True
            else:
                return False
        except AdvisorWrongSetting as e:
            raise CustomException(str(e), status_code = status.HTTP_400_BAD_REQUEST)

    def get(self, request, format = None):
        """
        Get all task objects.
        """
        query_params = request.query_params
        filters = self.get_filters(query_params)
        queue = query_params.get('queue')
        if queue:
            taskpool_queryset = TaskPool.objects.all()
            queryset = self.paginate_queryset(taskpool_queryset)
            serializer = self.get_serializer(queryset, many = True,
                                             context = {'request': request})
            return self.get_paginated_response(serializer.data)


        if query_params and query_params.get('task_uuid'):
            if not self.exist_object(**query_params):
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
            logger.debug("ssadvisor@views@TaskList@get@filters@%s" % filters)
            queryset = self.paginate_queryset(self.get_queryset(filters))
            serializer = self.get_serializer(queryset, many = True,
                                             context = {'request': request})
            return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a task instance.
        """
        serializer = TaskSerializer(data = request.data,
                                    context = {'request': request})
        if serializer.is_valid():
            task = serializer.create(serializer.validated_data)
            serializer = TaskSerializer(task, context = {'request': request})
            task_uuid = serializer.task_uuid
            submit_job.delay(task_uuid)
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class TaskDetail(generics.GenericAPIView):
    """
    Retrieve, update a task instance.
    """
    permission_classes = (permissions.IsAuthenticated,
                          CustomDjangoModelPermissions,
                          IsOwnerOrAdmin,)
    serializer_class = TaskSerializer
    queryset = Task.objects
    lookup_field = 'task_uuid'

    def get_object(self, task_uuid):
        try:
            obj = self.queryset.get(pk = task_uuid)
            self.check_object_permissions(self.request, obj)
            return obj
        except Task.DoesNotExist:
            raise CustomException("Not Found the Task.", status_code = status.HTTP_404_NOT_FOUND)

    def get(self, request, task_uuid):
        """
        Retrieve task information for a specified task instance.
        """
        task = self.get_object(task_uuid)
        serializer = TaskSerializer(task, context = {'request': request})
        update_jobstatus.delay(task_uuid = serializer.task_uuid)

        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        })

    def put(self, request, task_uuid):
        """
        Modify task information.
        """
        task = self.get_object(task_uuid)
        serializer = TaskSerializer(task, data = request.data,
                                    context = {'request': request},
                                    partial = True)
        if serializer.is_valid():
            task = serializer.update(task, serializer.validated_data)
            serializer = TaskSerializer(task, context = {'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class SettingList(generics.GenericAPIView):
    """
    List all setting objects, or create a new setting.
    """
    pagination_class = CustomPagination
    serializer_class = SettingSerializer
    permission_classes = (permissions.IsAuthenticated,
                          CustomDjangoModelPermissions,
                          permissions.IsAdminUser)
    queryset = AdvisorSetting.objects.all().order_by('name')
    lookup_field = 'setting_uuid'
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    def get_queryset(self, filters = None):
        try:
            if filters:
                return AdvisorSetting.objects.all().filter(**filters).order_by('name', 'is_active')
            else:
                return AdvisorSetting.objects.all().order_by('name', 'is_active')
        except AdvisorSetting.DoesNotExist:
            raise CustomException("Not Found the Settings.", status_code = status.HTTP_404_NOT_FOUND)

    def get(self, request, format = None):
        """
        Get all setting objects.
        """
        query_params = request.query_params

        filters = {}
        is_active = query_params.get('is_active')
        advisor_home = query_params.get('advisor_home')
        if is_active:
            filters.update({
                'is_active': True if is_active.upper() == 'TRUE' else FALSE,
            })
        if advisor_home:
            filters.update({
                'advisor_home': advisor_home
            })

        queryset = self.paginate_queryset(self.get_queryset(filters))
        serializer = self.get_serializer(queryset, many = True,
                                         context = {'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a setting instance.
        """
        serializer = SettingSerializer(data = request.data,
                                       context = {'request': request})
        if serializer.is_valid():
            setting = serializer.create(serializer.validated_data)
            serializer = SettingSerializer(setting, context = {'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class SettingDetail(generics.GenericAPIView):
    """
    Retrieve, update a setting instance.
    """
    permission_classes = (permissions.IsAuthenticated,
                          CustomDjangoModelPermissions,
                          IsOwnerOrAdmin,)
    serializer_class = SettingSerializer
    queryset = AdvisorSetting.objects
    lookup_field = 'setting_uuid'

    def get_object(self, setting_uuid):
        try:
            obj = self.queryset.get(setting_uuid = setting_uuid)
            self.check_object_permissions(self.request, obj)
            return obj
        except AdvisorSetting.DoesNotExist:
            raise CustomException("Not Found the Setting.", status_code = status.HTTP_404_NOT_FOUND)

    def get(self, request, setting_uuid):
        """
        Retrieve setting information for a specified setting instance.
        """
        setting = self.get_object(setting_uuid)
        serializer = SettingSerializer(setting, context = {'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        })

    def put(self, request, setting_uuid):
        """
        Modify setting information.
        """
        setting = self.get_object(setting_uuid = setting_uuid)
        serializer = SettingSerializer(setting, data = request.data,
                                       context = {'request': request},
                                       partial = True)
        if serializer.is_valid():
            setting = serializer.update(setting, serializer.validated_data)
            serializer = SettingSerializer(setting, context = {'request': request})
            return Response({
                "status": "Updated Success",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class TaskPoolList(generics.GenericAPIView):
    """
    List all task objects, or create a new task.
    """
    pagination_class = CustomPagination
    permission_classes = (permissions.IsAuthenticated,
                          CustomDjangoModelPermissions,
                          permissions.IsAdminUser)
    queryset = Task.objects.all().order_by('-created_time')
    lookup_field = 'task_uuid'
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.request.query_params.get('queue'):
            return TaskPoolSerializer
        return TaskSerializer

    def exist_object(self, **kwargs):
        new_kwargs = {}
        for key in kwargs.keys():
            if key in ('task_uuid'):
                if len(kwargs.get(key)) > 1:
                    return False
                else:
                    new_kwargs[key] = kwargs.get(key)[0]

        if new_kwargs:
            try:
                logger.debug("TaskList@exist_object@new_kwargs:%s" % str(new_kwargs))
                logger.debug("TaskList@exist_object@objects:%s" % str(self.queryset.get(**new_kwargs)))
                return self.queryset.get(**new_kwargs)
            except Task.DoesNotExist:
                return False

    def get_queryset(self, filters = None):
        try:
            if filters:
                return Task.objects.all().filter(**filters).order_by('-created_time')
            else:
                return Task.objects.all().order_by('-created_time')
        except Task.DoesNotExist:
            raise CustomException("Not Found the Tasks.", status_code = status.HTTP_404_NOT_FOUND)

    def get_filters(self, query_params):
        filters = {}
        created_time = query_params.get('created_time')
        finished_time = query_params.get('finished_time')
        progress_percentage = query_params.get('progress', 0)
        patient_uuid = query_params.get('patient_uuid')
        username = query_params.get('username')
        relationship = query_params.get('relationship')

        if created_time:
            filters.update({
                'created_time__gt': created_time,
            })
        if finished_time:
            filters.update({
                'finished_time__lt': finished_time,
            })
        if patient_uuid:
            filters.update({
                'patient__patient_uuid__lt': patient_uuid,
            })
        if progress_percentage is not None:
            try:
                filters.update({
                    'progress_percentage__gte': int(progress_percentage)
                })
            except:
                raise CustomException('Wrong query_params: progress.',
                                      status_code = status.HTTP_400_BAD_REQUEST)
        if username:
            filters.update({'user__username': username})
        if relationship:
            filters.update({'usertask__relationship': relationship})
        return filters

    def check_task_pool_valid(self, max_task_num):
        try:
            if TaskPool.objects.count() < max_task_num:
                return True
            else:
                return False
        except AdvisorWrongSetting as e:
            raise CustomException(str(e), status_code = status.HTTP_400_BAD_REQUEST)

    def get(self, request, format = None):
        """
        Get all task objects.
        """
        query_params = request.query_params
        filters = self.get_filters(query_params)
        queue = query_params.get('queue')
        if queue:
            taskpool_queryset = TaskPool.objects.all()
            queryset = self.paginate_queryset(taskpool_queryset)
            serializer = self.get_serializer(queryset, many = True,
                                             context = {'request': request})
            return self.get_paginated_response(serializer.data)


        if query_params and query_params.get('task_uuid'):
            if not self.exist_object(**query_params):
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
            logger.debug("ssadvisor@views@TaskList@get@filters@%s" % filters)
            print(filters)
            queryset = self.paginate_queryset(self.get_queryset(filters))
            serializer = self.get_serializer(queryset, many = True,
                                             context = {'request': request})
            return self.get_paginated_response(serializer.data)

    def post(self, request):
        """
        Create a task instance.
        """
        serializer = TaskSerializer(data = request.data,
                                    context = {'request': request})
        if serializer.is_valid():
            task = serializer.create(serializer.validated_data)
            serializer = TaskSerializer(task, context = {'request': request})
            return Response({
                "status": "success",
                "status_code": status.HTTP_201_CREATED,
                "data": serializer.data
            })
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class TaskPoolDetail(generics.GenericAPIView):
    """
    Retrieve, update a taskpool instance.
    """
    permission_classes = (permissions.IsAuthenticated,
                          CustomDjangoModelPermissions,
                          IsOwnerOrAdmin,)
    serializer_class = TaskPoolSerializer
    queryset = TaskPool.objects
    lookup_field = 'taskpool_uuid'

    def get_object(self, taskpool_uuid):
        try:
            obj = self.queryset.get(taskpool_uuid = taskpool_uuid)
            self.check_object_permissions(self.request, obj)
            return obj
        except TaskPool.DoesNotExist:
            raise CustomException("Not Found the Task Pool Instance.", status_code = status.HTTP_404_NOT_FOUND)

    def get(self, request, taskpool_uuid):
        """
        Retrieve taskpool information for a specified taskpool instance.
        """
        taskpool = self.get_object(taskpool_uuid)
        serializer = TaskPoolSerializer(taskpool, context = {'request': request})
        return Response({
            "status": "Success",
            "status_code": status.HTTP_200_OK,
            "data": serializer.data
        })
