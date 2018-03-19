# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import logging
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import (MaxValueValidator, MinValueValidator)
from sscobweb.models import Package

logger = logging.getLogger(__name__)


class AdvisorSetting(models.Model):
    setting_uuid = models.CharField(max_length=36, primary_key=True)
    name = models.CharField(max_length=16)
    summary = models.TextField(null=True)
    advisor_home = models.CharField(max_length=255)
    is_active = models.BooleanField(null=False, default=False)
    max_task_num = models.PositiveSmallIntegerField(default=10,
                                                    validators=[MaxValueValidator(100),])

    class Meta:
        ordering = ('name',)
        permissions = (("list_setting", "can list setting instance(s)"),)

    def __str__(self):
        return "%s" % (self.name)


class Patient(models.Model):
    patient_uuid = models.CharField(max_length=36, primary_key=True)
    case_id = models.CharField(max_length=32, unique=True)
    patient_name = models.CharField(max_length=32)
    name_alias = models.CharField(max_length=32)
    birth_date = models.DateField(null=True)
    gender = models.NullBooleanField(null=True)
    created_time = models.DateTimeField(null=True)
    summary = models.TextField(null=True)
    # One user vs. Several patients
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return '%s-%s' % (self.patient_uuid, self.case_id)

    class Meta:
        permissions = (("list_patient", "can list patient instance(s)"),)
        ordering = ('created_time', 'case_id', 'birth_date')


class File(models.Model):
    file_uuid = models.CharField(max_length=36, primary_key=True)
    file_id = models.CharField(max_length=32, unique=True)
    file_name = models.CharField(max_length=128)
    file_path = models.CharField(max_length=255)
    file_md5sum = models.CharField(max_length=32)
    created_time = models.DateTimeField(null=True)
    size = models.PositiveIntegerField()
    owners = models.ManyToManyField(
        User,
        through='UserFile',
        through_fields=('file', 'user')
    )
    # One patient vs. Several files
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    def __str__(self):
        return '%s-%s' % (self.file_uuid, self.file_name)

    class Meta:
        ordering = ('created_time', 'file_name', 'size')
        permissions = (("list_file", "can list file instance(s)"),)


class Task(models.Model):
    task_uuid = models.CharField(max_length=36, primary_key=True)
    task_name = models.CharField(max_length=128)
    summary = models.TextField(null=True)
    created_time = models.DateTimeField(null=True)
    finished_time = models.DateTimeField(null=True)
    # progress_percentage == 0: Running Task
    # progress_percentage == -1: New Task
    # progress_percentage == -2: Error Task
    progress_percentage = models.IntegerField(default=-1,
                                              validators=[MaxValueValidator(100), MinValueValidator(-2)])
    jobstatus = models.CharField(max_length=16, null=True)    # Job Status
    status_code = models.IntegerField()
    msg = models.TextField(null=True)
    args = models.TextField(null=True)
    # 必须保存为绝对路径，但是生成此路径时依据AdvisorSetting中的advisor_home
    # 用于生成job file的变量配置文件
    config_path = models.CharField(max_length=255, unique=True)
    output_path = models.CharField(max_length=255, unique=True)
    log_path = models.CharField(max_length=255, unique=True)
    files = models.ManyToManyField(File)
    # Task优先级，Level值越低级别越高
    priority_level = models.PositiveSmallIntegerField(default=10,
                                                      validators=[MaxValueValidator(10),])
    # One patient vs. Several tasks
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    owners = models.ManyToManyField(
        User,
        through='UserTask',
        through_fields=('task', 'user')
    )
    # One patient vs. Several tasks
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    def __str__(self):
        return '%s-%s' % (self.task_uuid, self.task_name)

    class Meta:
        ordering = ('created_time', 'task_name')
        permissions = (("list_task", "can list task instance(s)"),)


class TaskPool(models.Model):
    """
    保持与SGE队列一致，用于循环查询更新任务状态
    TaskPool最大行数即任务数由Settings.max_task_num指定，默认为10
    """
    task_pool_uuid = models.CharField(max_length=36, primary_key=True)
    task = models.OneToOneField(Task, on_delete=models.CASCADE)
    # Drmaa Job ID
    jobid = models.CharField(max_length=32, unique=True)
    jobstatus = models.CharField(max_length=255, null=True)
    # 状态更新时间
    updated_time = models.DateTimeField(null=True)
    # 用于计算percentage
    result_file_flags = models.TextField(null=True)

    class Meta:
        ordering = ('jobid', )
        permissions = (("list_taskpool",
                        "can list task instance(s) in taskpool"),)


class Report(models.Model):
    report_uuid = models.CharField(max_length=36, primary_key=True)
    report_name = models.CharField(max_length=128)
    checked = models.BooleanField(null=False, default=False)
    created_time = models.DateTimeField(null=True)
    checked_time = models.DateTimeField(null=True)
    # One task vs. One report
    task = models.OneToOneField(Task, on_delete=models.CASCADE)
    users = models.ManyToManyField(
        User,
        through='UserReport',
        through_fields=('report', 'user')
    )

    def __str__(self):
        return '%s-%s' % (self.report_uuid, self.report_name)

    class Meta:
        ordering = ('report_name', 'created_time', '-checked')
        permissions = (("list_report", "can list report instance(s)"),)


class UserReport(models.Model):
    RELATIONSHIPS = (
        ('checked_user', 'CHECKED_USER'),
        ('CHECKED_USER', 'CHECKED_USER'),
        ('owner', 'OWNER'),
        ('OWNER', 'OWNER'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    relationship = models.CharField(choices=RELATIONSHIPS, max_length=16)

    class Meta:
        permissions = (("list_userreport",
                        "can list all userreport relationship(s)"),)


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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    relationship = models.CharField(choices=RELATIONSHIPS, max_length=16)
    mode = models.CharField(choices=MODE, max_length=3)

    class Meta:
        permissions = (("list_userfile",
                        "can list all userfile relationship(s)"),)


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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    relationship = models.CharField(choices=RELATIONSHIPS, max_length=16)
    mode = models.CharField(choices=MODE, max_length=3)

    class Meta:
        permissions = (("list_usertask",
                        "can list all usertask relationship(s)"),)
