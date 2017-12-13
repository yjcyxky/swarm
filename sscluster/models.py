# -*- coding: utf-8 -*-
import logging, copy
from datetime import datetime
from django.db import models
from django.apps import apps
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

class ToDoList(models.Model):
    item_name = models.CharField(max_length = 32)
    item_title = models.CharField(max_length = 32)
    item_content = models.TextField(null = True)
    created_time = models.DateTimeField(auto_now_add=True)
    checked_status = models.BooleanField(null = False, default = False)
    finished_time = models.DateTimeField(null = True)
    user = models.ForeignKey(User)

    def __str__(self):
        return '%s-%s' % (self.id, self.item_name)

    class Meta:
        ordering = ('checked_status', 'created_time', 'user')

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
    jobid = models.CharField(max_length = 32, unique = True)
    jobname = models.CharField(max_length = 128)
    user = models.ForeignKey(User)
    # user = models.CharField(max_length = 32)
    # group = models.ForeignKey(Group)
    group = models.CharField(max_length = 32)
    # owner = models.ForeignKey(User)
    owner = models.CharField(max_length = 32)
    queue = models.CharField(max_length = 32)
    ctime = models.DateTimeField(null = True)    # Time job was created
    qtime = models.DateTimeField(null = True)    # Time job was queued
    etime = models.DateTimeField(null = True)    # Time job became eligible to run
    start = models.DateTimeField(db_index = True, null = True)    # Time job started to run
    end = models.DateTimeField(db_index = True, null = True)
    exec_host = models.TextField(null = True)
    resource_list_neednodes = models.CharField(max_length = 256, null = True)
    resource_list_nodect = models.CharField(max_length = 256, null = True)
    resource_list_nodes = models.CharField(max_length = 256, null = True)
    resource_list_walltime = models.CharField(max_length = 16, null = True)
    session = models.CharField(max_length = 32, null = True)
    unique_node_count = models.PositiveIntegerField(null = True)
    exit_status = models.IntegerField(null = True)
    resources_used_cput = models.CharField(max_length = 16, null = True)
    resources_used_mem = models.PositiveIntegerField(null = True)
    resources_used_vmem = models.PositiveIntegerField(null = True)
    resources_used_walltime = models.CharField(max_length = 16, null = True)
    cpus_num = models.PositiveIntegerField(null = True)
    total_execution_slots = models.PositiveIntegerField(null = True)
    cluster_uuid = models.ForeignKey(Cluster)

    def __str__(self):
        return '%s-%s' % (self.jobid, self.jobname)

    class Meta:
        ordering = ('jobid', 'owner')

    # Record Marker
    # A --- abort --- (Job has been aborted by the server)
    # C --- checkpoint --- (Job has been checkpointed and held)
    # D --- delete --- (Job has been deleted)
    # E --- exit --- (Job has exited(either successfully or unsuccessfully))
    # Q --- queue --- (Job has been submitted/queued)
    # R --- rerun --- (Attempt to rerun the job has been made)
    # S --- start --- (Attempt to start the job has been made (if the job fails to properly start, it may have multiple job start records))
    # T --- restart --- (Attempt to restart the job (from checkpoint) has been made (if the job fails to properly start, it may have multiple job start records))
