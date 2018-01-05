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
from ssfalcon import (aggregator_views, events_views)

urlpatterns = [
    url(r'^aggregators$',
        aggregator_views.AggregatorList.as_view(),
        name = 'aggregator-list'),
    url(r'^aggregators/(?P<aggregator_id>[0-9]+)$',
        aggregator_views.AggregatorDetail.as_view(),
        name = 'aggregator-detail'),
    url(r'^hostgroup/(?P<hostgroup_id>[0-9]+)/aggregators$',
        aggregator_views.AggregatorGroupList.as_view(),
        name = 'hostgroup-detail'),
    url(r'^alarm/eventcases$',
        events_views.EventCaseList.as_view(),
        name = 'event-case-list'),
    url(r'^alarm/event_note$',
        events_views.EventNoteList.as_view(),
        name = 'event-note-list'),
    url(r'^alarm/events$',
        events_views.EventList.as_view(),
        name = 'event-list'),
]
