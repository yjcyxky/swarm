# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import logging
import re
import datetime
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework import status
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator
from sscluster.models import (Cluster, JobLog, ToDoList)

logger = logging.getLogger(__name__)

def check_name(name, msg = 'Not a valid name.'):
    RE = re.compile("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-\_]*[A-Za-z0-9])$")
    match = re.match(RE, name)
    if match is None:
        raise serializers.ValidationError(msg)

def check_job_name(job_name):
    check_name(job_name, 'Not a valid job name.')

def check_cluster_name(cluster_name):
    check_name(cluster_name, 'Not a valid cluster name.')

class ClusterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Cluster
        fields = ('cluster_uuid', 'cluster_name', 'total_nodes', 'server_status', 'total_memory_size',
                  'total_storage_size', 'management_node_uuid')
        lookup_field = 'cluster_uuid'

    def create(self, validated_data):
        cluster = Cluster.objects.create(**validated_data)
        cluster.save()
        return cluster

    def update(self, instance, validated_data):
        instance.total_nodes = validated_data.get('total_nodes', instance.total_nodes)
        instance.total_memory_size = validated_data.get('total_memory_size', instance.total_memory_size)
        instance.total_storage_size = validated_data.get('total_storage_size', instance.total_storage_size)
        instance.server_status = validated_data.get('server_status', instance.server_status)
        instance.management_node_uuid = validated_data.get('management_node_uuid', instance.management_node_uuid)
        instance.save()
        return instance

class ToDoListSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset = User.objects.all())

    class Meta:
        model = ToDoList
        fields = ('id', 'item_name', 'item_title', 'item_content', 'created_time',
                  'finished_time', 'checked_status', 'user')
        lookup_field = 'id'

    def create(self, validated_data):
        user = validated_data.pop('user')
        todolist = ToDoList.objects.create(user = user, **validated_data)
        todolist.save()
        return todolist

    def update(self, instance, validated_data):
        instance.checked_status = validated_data.get('checked_status', instance.checked_status)
        instance.finished_time = validated_data.get('finished_time', instance.finished_time)
        instance.save()
        return instance


class JobLogSerializer(serializers.ModelSerializer):
    cluster = ClusterSerializer(read_only = True)
    user = serializers.PrimaryKeyRelatedField(queryset = User.objects.all())

    class Meta:
        model = JobLog
        fields = ('job_uuid', 'jobid', 'jobname', 'user', 'group', 'owner', 'queue',
                  'ctime', 'qtime', 'etime', 'start', 'end', 'exec_host',
                  'resource_list_neednodes', 'resource_list_nodect',
                  'resource_list_nodes', 'resource_list_walltime', 'session',
                  'unique_node_count', 'exit_status', 'resources_used_cput',
                  'resources_used_mem', 'resources_used_vmem', 'resources_used_walltime',
                  'cpus_num', 'total_execution_slots', 'cluster')
        lookup_field = 'job_uuid'

    def create(self, validated_data):
        user = validated_data.pop('user')
        job_log = JobLog.objects.create(user = user, **validated_data)
        job_log.save()
        return job_log

    def update(self, instance, validated_data):
        instance.exit_status = validated_data.get('exit_status', instance.exit_status)
        instance.resources_used_cput = validated_data.get('resources_used_cput', instance.resources_used_cput)
        instance.resources_used_mem = validated_data.get('resources_used_mem', instance.resources_used_mem)
        instance.resources_used_vmem = validated_data.get('resources_used_vmem', instance.resources_used_vmem)
        instance.resources_used_walltime = validated_data.get('resources_used_walltime', instance.resources_used_walltime)
        instance.end = validated_data.get('end', instance.end)
        instance.save()
        return instance

    def validate(self, data):
        """
        Check that the finished_datetime is before the submitted_datetime.
        """
        if data.get('start') and data.get('end'):
            if data.get('end') <= data.get('start'):
                raise serializer.ValidationError("start must occur after end.")
        return data

class JobLogCountSerializer(serializers.ModelSerializer):
    records_count = serializers.IntegerField(min_value = 0)

    def to_representation(self, instance):
        print('sscluster@serializers@JobLogCountSerializer@to_representation@', instance)
        request = self.context.get('request')
        return {
            'owner': instance.get('joblog__owner'),
            'cluster_uuid': instance.get('joblog__cluster_uuid'),
            'records_count': instance.get('records_count'),
            'used_cput': instance.get('used_cput'),
            'used_mem': instance.get('used_mem'),
            'used_vmem': instance.get('used_vmem'),
            'month': instance.get('month', None),
            'year': instance.get('year', None),
            'week': instance.get('week', None),
            'day': instance.get('day', None),
            'start': request.query_params.get('start', '2012-12-12 08:00:00'),
            'end': request.query_params.get('end', '2100-12-12 08:00:00'),
        }

    class Meta:
        model = User
        fields = ('records_count', 'owner', 'group', 'cluster_uuid', 'start',
                  'end', 'used_cput', 'used_mem', 'used_vmem')
        read_only_fields = ('records_count', 'owner', 'group', 'cluster_uuid',
                            'start', 'end', 'used_cput', 'used_mem', 'used_vmem')
