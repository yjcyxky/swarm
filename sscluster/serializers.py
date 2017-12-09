import logging
import re
import datetime
from rest_framework import serializers
from rest_framework import status
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator
from sscluster.models import (Cluster, JobLog)

logger = logging.getLogger(__name__)

def check_name(name, msg = 'Not a valid name.'):
    RE = re.compile("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-\_]*[A-Za-z0-9])$")
    match = re.match(RE, name)
    if match is None:
        raise serializers.ValidationError(msg)

def check_job_name(job_name):
    check_name(hostname, 'Not a valid job name.')

def check_cluster_name(cluster_name):
    check_name(cluster_name, 'Not a valid cluster name.')

class ClusterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Cluster
        fields = ('cluster_uuid', 'cluster_name', 'total_nodes', 'server_status', 'total_memory_size',
                  'total_storage_size', 'management_node_uuid')
        lookup_field = 'cluster_uuid'

    def create(self, validated_data):
        cluster = cluster.objects.create(**validated_data)
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


class JobLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobLog
        fields = ('job_uuid', 'job_id', 'job_name', 'job_owner', 'used_cpu_time',
                  'job_state', 'session_id', 'nodes_num', 'cpus_num', 'memory_size',
                  'queue_name', 'submitted_datetime', 'finished_datetime', 'cluster_uuid')
        lookup_field = 'job_uuid'

    def create(self, validated_data):
        job_log = JobLog.objects.create(**validated_data)
        job_log.save()
        return job_log

    def update(self, instance, validated_data):
        instance.job_state = validated_data.get('job_state', instance.job_state)
        instance.finished_datetime = validated_data.get('finished_datetime', instance.finished_datetime)
        instance.used_cpu_time = validated_data.get('used_cpu_time', instance.userd_cpu_time)
        instance.save()
        return instance

    def validate(self, data):
        """
        Check that the finished_datetime is before the submitted_datetime.
        """
        if data.get('finished_datetime') and data.get('submitted_datetime'):
            if data.get('finished_datetime') <= data.get('submitted_datetime'):
                raise serializer.ValidationError("finished_datetime must occur after submitted_datetime.")
        return data
