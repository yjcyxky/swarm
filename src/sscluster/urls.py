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
from sscluster import views

urlpatterns = [
    url(r'^clusters$',
        views.ClusterList.as_view(),
        name = 'cluster-list'),
    url(r'^clusters/(?P<cluster_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.ClusterDetail.as_view(),
        name = 'cluster-detail'),
    url(r'^joblogs$',
        views.JobLogList.as_view(),
        name = 'job-log-list'),
    url(r'^joblogs/count$',
        views.JobLogCount.as_view(),
        name = 'job-log-count'),
    url(r'^joblogs/(?P<job_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.JobLogDetail.as_view(),
        name = 'job-log-detail'),
    url(r'^joblogs/(?P<jobid>^[0-9]+\.[a-zA-Z0-9_\-]+$)$',
        views.JobLogDetail.as_view(),
        name = 'job-log-detail'),
    url(r'^todolist/(?P<pk>[0-9]+)$',
        views.ToDoListDetail.as_view(),
        name = 'todolist-detail'),
    url(r'^todolist$',
        views.ToDoListList.as_view(),
        name = 'todolist-list'),
]
