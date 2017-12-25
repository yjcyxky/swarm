# -*- coding: utf-8 -*-
import logging
import copy
import uuid
import os
from datetime import datetime
from django.db import models
from django.apps import apps
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from sscobweb.models import Package

logger = logging.getLogger(__name__)

def get_templ_path(instance, filename):
    return os.path.join('templates', 'advisor_task.sh')


class Setting(models.Model):
    setting_uuid = models.CharField(max_length = 36, primary_key = True)
    name = models.CharField(max_length = 16)
    summary = models.TextField(null = True)
    advisor_home = models.CharField(max_length = 255)
    is_active = models.BooleanField(null = False, default = False)
    bash_templ = models.FileField(max_length = 32, upload_to = get_templ_path)
    max_task_num = models.PositiveSmallIntegerField(default = 10,
                                                    validators=[MaxValueValidator(100),])

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return "%s" % (self.name)


class Patient(models.Model):
    patient_uuid = models.CharField(max_length = 36, primary_key = True)
    case_id = models.CharField(max_length = 32, unique = True)
    patient_name = models.CharField(max_length = 32)
    name_alias = models.CharField(max_length = 32)
    birth_date = models.DateField(null = True)
    gender = models.NullBooleanField(null = True)
    created_time = models.DateTimeField(null = True)
    summary = models.TextField(null = True)
    user = models.ForeignKey(User, on_delete = models.CASCADE) # One user vs. Several patients

    def __str__(self):
        return '%s-%s' % (self.patient_uuid, self.case_id)

    class Meta:
        ordering = ('created_time', 'case_id', 'birth_date')


class File(models.Model):
    file_uuid = models.CharField(max_length = 36, primary_key = True)
    file_id = models.CharField(max_length = 32, unique = True)
    file_name = models.CharField(max_length = 128)
    file_path = models.CharField(max_length = 255)
    file_md5sum = models.CharField(max_length = 32)
    created_time = models.DateTimeField(null = True)
    size = models.PositiveIntegerField()
    owners = models.ManyToManyField(
        User,
        through = 'UserFile',
        through_fields = ('file', 'user')
    )
    patient = models.ForeignKey(Patient, on_delete = models.CASCADE) # One patient vs. Several files

    def __str__(self):
        return '%s-%s' % (self.file_uuid, self.file_name)

    class Meta:
        ordering = ('created_time', 'file_name', 'size')


class Task(models.Model):
    task_uuid = models.CharField(max_length = 36, primary_key = True)
    task_name = models.CharField(max_length = 128)
    summary = models.TextField(null = True)
    created_time = models.DateTimeField(null = True)
    finished_time = models.DateTimeField(null = True)
    progress_percentage = models.PositiveSmallIntegerField(default = 0,
                                                           validators=[MaxValueValidator(100),])
    status_code = models.IntegerField()
    msg = models.TextField(null = True)
    args = models.TextField(null = True)
    config_path = models.CharField(max_length = 255, unique = True)
    output_path = models.CharField(max_length = 255, unique = True)
    log_path = models.CharField(max_length = 255, unique = True)
    files = models.ManyToManyField(File)
    package = models.ForeignKey(Package, on_delete = models.CASCADE) # One patient vs. Several tasks
    owners = models.ManyToManyField(
        User,
        through = 'UserTask',
        through_fields = ('task', 'user')
    )
    patient = models.ForeignKey(Patient, on_delete = models.CASCADE) # One patient vs. Several tasks

    def __str__(self):
        return '%s-%s' % (self.task_uuid, self.task_name)

    class Meta:
        ordering = ('created_time', 'task_name')


class TaskPool(models.Model):
    """
    保持与SGE队列一致，用于循环查询更新任务状态
    TaskPool最大行数即任务数由Settings.max_task_num指定，默认为10
    """
    task_pool_uuid = models.CharField(max_length = 36, primary_key = True)
    task = models.OneToOneField(Task, on_delete = models.CASCADE)
    # Drmaa Job ID
    job_id = models.CharField(max_length = 32, unique = True)

    class Meta:
        ordering = ('job_id', )


class Report(models.Model):
    report_uuid = models.CharField(max_length = 36, primary_key = True)
    report_name = models.CharField(max_length = 128)
    checked = models.BooleanField(null = False, default = False)
    created_time = models.DateTimeField(null = True)
    checked_time = models.DateTimeField(null = True)
    task = models.OneToOneField(Task, on_delete = models.CASCADE) # One task vs. One report
    users = models.ManyToManyField(
        User,
        through = 'UserReport',
        through_fields = ('report', 'user')
    )

    def __str__(self):
        return '%s-%s' % (self.report_uuid, self.report_name)

    class Meta:
        ordering = ('report_name', 'created_time', '-checked')


class UserReport(models.Model):
    RELATIONSHIPS = (
        ('checked_user', 'CHECKED_USER'),
        ('CHECKED_USER', 'CHECKED_USER'),
        ('owner', 'OWNER'),
        ('OWNER', 'OWNER'),
    )
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    report = models.ForeignKey(Report, on_delete = models.CASCADE)
    relationship = models.CharField(choices = RELATIONSHIPS, max_length = 16)


class UserFile(models.Model):
    RELATIONSHIPS = (
        ('observer', 'OBSERVER'),
        ('OBSERVER', 'OBSERVER'),
        ('manipulator', 'MANIPULATOR'),
        ('MANIPULATOR', 'MANIPULATOR'),
        ('owner', 'OWNER'),
        ('OWNER', 'OWNER'),
    )
    MODE = (
        ('421', '421'),  # rwx，可读，可写，可删除
        ('420', '420'),
        ('400', '400'),
    )
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    file = models.ForeignKey(File, on_delete = models.CASCADE)
    relationship = models.CharField(choices = RELATIONSHIPS, max_length = 16)
    mode = models.CharField(choices = MODE, max_length = 3)


class UserTask(models.Model):
    RELATIONSHIPS = (
        ('observer', 'OBSERVER'),
        ('OBSERVER', 'OBSERVER'),
        ('manipulator', 'MANIPULATOR'),
        ('MANIPULATOR', 'MANIPULATOR'),
        ('owner', 'OWNER'),
        ('OWNER', 'OWNER'),
    )
    MODE = (
        ('421', '421'),    # rwx，可读，可写，可删除
        ('420', '420'),
        ('400', '400'),
    )
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    task = models.ForeignKey(Task, on_delete = models.CASCADE)
    relationship = models.CharField(choices = RELATIONSHIPS, max_length = 16)
    mode = models.CharField(choices = MODE, max_length = 3)
