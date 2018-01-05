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
from sshostmgt import views

urlpatterns = [
    url(r'^ipmi$',
        views.IPMIList.as_view(),
        name = 'ipmi-list'),
    url(r'^ipmi/(?P<ipmi_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.IPMIDetail.as_view(),
        name = 'ipmi-detail'),
    url(r'^tags$',
        views.TagList.as_view(),
        name = 'tag-list'),
    url(r'^tags/(?P<tag_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.TagDetail.as_view(),
        name = 'tag-detail'),
    url(r'^hosts$',
        views.HostList.as_view(),
        name = 'host-list'),
    url(r'^hosts/(?P<host_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.HostDetail.as_view(),
        name = 'host-detail'),
    url(r'^storages$',
        views.StorageList.as_view(),
        name = 'storage-list'),
    url(r'^storages/(?P<storage_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.StorageDetail.as_view(),
        name = 'host-detail'),
]
