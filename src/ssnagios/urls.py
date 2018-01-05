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
from ssnagios import views

urlpatterns = [
    url(r'^errors/$',
        views.AggregatorList.as_view(),
        name = 'aggregator-list'),
    url(r'^errors/(?P<hostname>[0-9a-zA-Z_\-]+)$',
        views.AggregatorDetail.as_view(),
        name = 'aggregator-detail')
    url(r'^warnings/$',
        views.AggregatorDetail.as_view(),
        name = 'aggregator-detail')
    url(r'^info/$',
        views.AggregatorDetail.as_view(),
        name = 'aggregator-detail')
]
