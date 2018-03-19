# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

from django.conf.urls import url
from sscobweb import views

urlpatterns = [
    url(r'^channels$',
        views.ChannelList.as_view(),
        name='channel-list'),
    url(r'^channels/(?P<channel_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.ChannelDetail.as_view(),
        name='channel-detail'),
    url(r'^packages$',
        views.PackageList.as_view(),
        name='package-list'),
    url(r'^packages/(?P<pkg_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.PackageDetail.as_view(),
        name='package-detail'),
    url(r'^settings$',
        views.SettingList.as_view(),
        name='setting-list'),
    url(r'^settings/(?P<setting_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.SettingDetail.as_view(),
        name='setting-detail'),
]
