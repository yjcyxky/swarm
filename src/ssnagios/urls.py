# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

from django.conf.urls import url
from ssnagios import views

urlpatterns = [
    url(r'^notifications$',
        views.NotificationList.as_view(),
        name='notification-list'),
    url(r'^notifications/(?P<notification_id>[0-9]+)$',
        views.NotificationDetail.as_view(),
        name='notification-detail'),
    url(r'^hosts/(?P<hostname>[0-9a-zA-Z_\-\.]+)$',
        views.HostDetail.as_view(),
        name='host-detail'),
]
