# -*- coding: utf-8 -*-
import logging, copy
from datetime import datetime
from django.db import models
from django.apps import apps
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

class Cluster(models.Model):
    cluster_uuid = models.CharField(max_length = 128, primary_key = True)
    cluster_name = models.CharField(max_length = 32)
    total_nodes = models.PositiveIntegerField()
    server_status = models.CharField(max_length = 10)
    total_memory_size = models.PositiveIntegerField()
    total_storage_size = models.PositiveIntegerField()
    management_node_uuid = models.CharField(max_length = 128)

    def __str__(self):
        return '%s-%s' % (self.cluster_uuid, self.cluster_name)

    class Meta:
        ordering = ('cluster_name',)

class JobLog(models.Model):
    job_uuid = models.CharField(max_length = 128, primary_key = True)
    job_id = models.CharField(max_length = 32, unique = True)
    job_name = models.CharField(max_length = 32)
    job_owner = models.ForeignKey(User)
    used_cpu_time = models.CharField(max_length = 64)
    job_state = models.CharField(max_length = 10, null = True, default = 'Queue')
    session_id = models.CharField(max_length = 32, unique = True)
    nodes_num = models.PositiveIntegerField(null = True)
    cpus_num = models.PositiveIntegerField(null = True)
    memory_size = models.PositiveIntegerField(null = True)
    queue_name = models.CharField(max_length = 32)
    submitted_datetime = models.CharField(max_length = 64)
    finished_datetime = models.CharField(max_length = 64)
    cluster_uuid = models.ForeignKey(Cluster)

    def __str__(self):
        return '%s-%s' % (self.job_id, self.job_name)

    class Meta:
        ordering = ('job_id', 'job_owner')
