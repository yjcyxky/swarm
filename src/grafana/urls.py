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
    url(r'^panel$',
        views.PanelList.as_view(),
        name='panel-list'),
    url(r'^panel/(?P<panel_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.PanelDetail.as_view(),
        name='panel-detail'),
]
