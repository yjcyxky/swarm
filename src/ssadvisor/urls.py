# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

from django.conf.urls import url, include
from rest_framework import routers
from ssadvisor import views

urlpatterns = [
    url(r'^patients$',
        views.PatientList.as_view(),
        name = 'patient-list'),
    url(r'^patients/(?P<patient_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.PatientDetail.as_view(),
        name = 'patient-detail'),
    url(r'^tasks$',
        views.TaskList.as_view(),
        name = 'task-list'),
    url(r'^tasks/(?P<task_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.TaskDetail.as_view(),
        name = 'task-detail'),
    url(r'^files/(?P<file_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.FileDetail.as_view(),
        name = 'file-detail'),
    url(r'^files$',
        views.FileList.as_view(),
        name = 'file-list'),
    url(r'^reports/(?P<report_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.ReportDetail.as_view(),
        name = 'report-detail'),
    url(r'^reports$',
        views.ReportList.as_view(),
        name = 'report-list'),
    url(r'^settings/(?P<setting_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.SettingDetail.as_view(),
        name = 'setting-detail'),
    url(r'^settings$',
        views.SettingList.as_view(),
        name = 'setting-list'),
]
