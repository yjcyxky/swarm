# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import logging
import os
import re
import datetime
import uuid
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework import status
from rest_framework.validators import UniqueValidator
from django.db import transaction
from django.core.validators import RegexValidator
from ssadvisor.models import (Patient, UserReport, Report, UserFile, File,
                              UserTask, Task, TaskPool, User, AdvisorSetting)
from ssadvisor.exceptions import CustomException
from ssadvisor.utils import get_settings

logger = logging.getLogger(__name__)

def check_name(name, msg = 'Not a valid name.'):
    RE = re.compile("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-\_]*[A-Za-z0-9])$")
    match = re.match(RE, name)
    if match is None:
        raise serializers.ValidationError(msg)

def check_report_name(report_name):
    check_name(report_name, 'Not a valid name.')

def check_value(items):
    if isinstance(items, dict):
        for key, value in items.items():
            if value is None:
                raise CustomException('None field %s' % name, status_code = status.HTTP_400_BAD_REQUEST)
    else:
        raise

class SettingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AdvisorSetting
        fields = ('setting_uuid', 'name', 'summary', 'is_active', 'advisor_home',
                  'max_task_num')
        lookup_field = 'setting_uuid'

    def create(self, validated_data):
        setting = AdvisorSetting.objects.create(**validated_data)
        setting.save()
        return setting

    def change_is_active(self, raw_is_active, is_active):
        if raw_is_active is True and is_active is False:
            raise CustomException('Valid Constraint: Must Be Sure that Only One Setting is Valid.')
        else:
            AdvisorSetting.objects.all().update(is_active = False)

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        self.change_is_active(instance.is_active, validated_data.get('is_active'))
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.summary = validated_data.get('summary', instance.summary)
        instance.advisor_home = validated_data.get('advisor_home', instance.advisor_home)
        instance.max_task_num = validated_data.get('max_task_num', instance.max_task_num)
        instance.save()
        return instance


class PatientSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True,
                                              default=serializers.CurrentUserDefault())

    class Meta:
        model = Patient
        fields = ('patient_uuid', 'created_time', 'case_id', 'patient_name',
                  'name_alias', 'birth_date', 'gender', 'summary', 'user')
        lookup_field = 'patient_uuid'

    def create(self, validated_data):
        patient = Patient.objects.create(**validated_data)
        patient.save()
        return patient

    def update(self, instance, validated_data):
        instance.case_id = validated_data.get('case_id', instance.case_id)
        instance.patient_name = validated_data.get('patient_name', instance.patient_name)
        instance.name_alias = validated_data.get('name_alias', instance.name_alias)
        instance.birth_date = validated_data.get('birth_date', instance.birth_date)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.summary = validated_data.get('summary', instance.summary)
        instance.user = validated_data.get('user', instance.user)
        instance.save()
        return instance


class UserTaskSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')
    task = serializers.ReadOnlyField(source='task.task_uuid')

    class Meta:
        model = UserTask
        fields = ('user', 'task', 'relationship', 'mode')


def gen_path(task_uuid):
    advisor_setting = get_settings(AdvisorSetting)
    advisor_home = advisor_setting.advisor_home
    config_path = os.path.join(advisor_home, task_uuid, 'config')
    output_path = os.path.join(advisor_home, task_uuid, 'results')
    log_path = os.path.join(advisor_home, task_uuid, 'logs')
    return config_path, output_path, log_path


class TaskSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset = Patient.objects.all(),
                                                 pk_field = serializers.UUIDField(format='hex_verbose'))
    owners = UserTaskSerializer(source = 'usertask_set', many = True,
                                read_only = True)

    class Meta:
        model = Task
        fields = ('task_uuid', 'task_name', 'summary', 'created_time', 'finished_time',
                  'progress_percentage', 'status_code', 'msg', 'config_path',
                  'output_path', 'log_path', 'files', 'package', 'owners', 'patient')
        lookup_field = 'task_uuid'
        depth = 1

    @transaction.atomic
    def create(self, validated_data):
        validated_data_clone = validated_data.copy()
        task_uuid = validated_data.get('task_uuid', uuid.uuid4())
        config_path, output_path, log_path = self.gen_path(task_uuid)
        validated_data_clone['config_path'] = config_path
        validated_data_clone['log_path'] = log_path
        validated_data_clone['output_path'] = output_path
        validated_data_clone['task_uuid'] = task_uuid
        task = Task.objects.create(**validated_data_clone)
        if 'owners' in self.initial_data:
            owners = self.initial_data.get('owners')
            for owner in owners:
                id = owner.get('user')
                relationship = owner.get('relationship')
                mode = owner.get('mode')
                items = {
                    'id': id,
                    'relationship': relationship,
                    'mode': mode
                }
                check_value(items)
                try:
                    user_instance = User.objects.get(pk = id)
                except:
                    raise CustomException('No Such User.', status_code = status.HTTP_400_BAD_REQUEST)

                UserTask(task = task, user = user_instance, mode = mode,
                         relationship = relationship).save()
            task.save()
        return task

    @transaction.atomic
    def update(self, instance, validated_data):
        if 'owners' in self.initial_data:
            UserTask.objects.filter(task = instance).delete()
            owners = self.initial_data.get('owners')
            for owner in owners:
                id = owner.get('user')
                relationship = owner.get('relationship')
                mode = owner.get('mode')
                items = {
                    'id': id,
                    'relationship': relationship,
                    'mode': mode
                }
                check_value(items)
                try:
                    new_user_instance = User.objects.get(pk = id)
                except:
                    raise CustomException('No Such User.', status_code = status.HTTP_400_BAD_REQUEST)
                UserTask(task = instance, user = new_user_instance, mode = mode,
                         relationship = relationship).save()
        instance.__dict__.update(**validated_data)
        instance.save()
        return instance


class TaskPoolSerializer(serializers.ModelSerializer):
    task = TaskSerializer(read_only = True)

    class Meta:
        model = TaskPool
        fields = ('task_pool_uuid', 'task', 'jobid', 'jobstatus', 'updated_time')

    def create(self, validated_data):
        taskpool = TaskPool.objects.create(**validated_data)
        taskpool.save()
        return taskpool


class UserFileSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')
    file = serializers.ReadOnlyField(source='file.file_uuid')

    class Meta:
        model = UserFile
        fields = ('user', 'file', 'relationship', 'mode')


class FileSerializer(serializers.HyperlinkedModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset = Patient.objects.all(),
                                                 pk_field = serializers.UUIDField(format='hex_verbose'))
    owners = UserFileSerializer(source = 'userfile_set', many = True,
                                read_only = True)

    class Meta:
        model = File
        fields = ('file_uuid', 'file_id', 'file_name', 'file_path', 'file_md5sum',
                  'created_time', 'size', 'owners', 'patient')
        lookup_field = 'file_uuid'
        depth = 1

    @transaction.atomic
    def create(self, validated_data):
        file = File.objects.create(**validated_data)
        if 'owners' in self.initial_data:
            owners = self.initial_data.get('owners')
            for owner in owners:
                id = owner.get('user')
                relationship = owner.get('relationship')
                mode = owner.get('mode')
                items = {
                    'id': id,
                    'relationship': relationship,
                    'mode': mode
                }
                check_value(items)
                try:
                    user_instance = User.objects.get(pk = id)
                except:
                    raise CustomException('No Such User.', status_code = status.HTTP_400_BAD_REQUEST)

                UserFile(file = file, user = user_instance, mode = mode,
                         relationship = relationship).save()
            file.save()
        return file

    @transaction.atomic
    def update(self, instance, validated_data):
        if 'owners' in self.initial_data:
            UserFile.objects.filter(file = instance).delete()
            owners = self.initial_data.get('owners')
            for owner in owners:
                id = owner.get('user')
                relationship = owner.get('relationship')
                mode = owner.get('mode')
                items = {
                    'id': id,
                    'relationship': relationship,
                    'mode': mode
                }
                check_value(items)
                try:
                    new_user_instance = User.objects.get(pk = id)
                except:
                    raise CustomException('No Such User.', status_code = status.HTTP_400_BAD_REQUEST)

                UserFile(file = instance, user = new_user_instance, mode = mode,
                         relationship = relationship).save()
        instance.__dict__.update(**validated_data)
        instance.save()
        return instance


class UserReportSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')
    report = serializers.ReadOnlyField(source='report.report_uuid')

    class Meta:
        model = UserReport
        fields = ('user', 'report', 'relationship')


class ReportSerializer(serializers.HyperlinkedModelSerializer):
    users = UserReportSerializer(source = 'userreport_set', many = True,
                                 read_only = True)
    task = serializers.PrimaryKeyRelatedField(queryset = Task.objects.all(),
                                              pk_field = serializers.UUIDField(format='hex_verbose'))

    class Meta:
        model = Report
        fields = ('report_uuid', 'report_name', 'checked', 'created_time',
                  'checked_time', 'task', 'users')
        lookup_field = 'report_uuid'
        depth = 1

    @transaction.atomic
    def create(self, validated_data):
        report = Report.objects.create(**validated_data)
        if 'users' in self.initial_data:
            users = self.initial_data.get('users')
            for user in users:
                id = user.get('user')
                relationship = user.get('relationship')
                items = {
                    'id': id,
                    'relationship': relationship,
                }
                check_value(items)
                try:
                    user_instance = User.objects.get(pk = id)
                except:
                    raise CustomException('No Such User.', status_code = status.HTTP_400_BAD_REQUEST)

                UserReport(report = report, user = user_instance,
                           relationship = relationship).save()
            report.save()
        return report

    @transaction.atomic
    def update(self, instance, validated_data):
        if 'users' in self.initial_data:
            UserReport.objects.filter(report = instance).delete()
            users = self.initial_data.get('users')
            for user in users:
                id = user.get('user')
                relationship = user.get('relationship')
                items = {
                    'id': id,
                    'relationship': relationship,
                }
                check_value(items)
                try:
                    new_user_instance = User.objects.get(pk = id)
                except:
                    raise CustomException('No Such User.', status_code = status.HTTP_400_BAD_REQUEST)

                UserReport(report = instance, user = new_user_instance,
                           relationship = relationship).save()
        instance.__dict__.update(**validated_data)
        instance.save()
        return instance
