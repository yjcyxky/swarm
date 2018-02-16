# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

from django.conf.urls import url
from ssganglia import views

urlpatterns = [
    url(r'^clusters/$',
        views.ClusterList.as_view(),
        name='cluster-list'),
    url(r'^clusters/(?P<clustername>[0-9a-zA-Z_\-]+)$',
        views.HostList.as_view(),
        name='host-list'),
    url(r'^hosts/(?P<hostname>[0-9a-zA-Z_\-\.]+)$',
        views.MetricList.as_view(),
        name='metric-list'),
    url(r'^hosts/(?P<hostname>[0-9a-zA-Z_\-\.]+)/(?P<metric>[0-9a-zA-Z_\-]+)$',
        views.MetricDetail.as_view(),
        name='metric-detail')
]
