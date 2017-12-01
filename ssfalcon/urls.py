"""sshostmgt URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
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
