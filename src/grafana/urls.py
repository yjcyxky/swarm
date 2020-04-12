# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

from django.conf.urls import url
from grafana import views

urlpatterns = [
    url(r'^panels$',
        views.PanelList.as_view(),
        name='panel-list'),
    url(r'^panels/(?P<panel_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.PanelDetail.as_view(),
        name='panel-detail'),
    url(r'^dashboards$',
        views.DashboardList.as_view(),
        name='dashboard-list'),
    url(r'^dashboards/(?P<dashboard_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.DashboardDetail.as_view(),
        name='dashboard-detail'),
]
