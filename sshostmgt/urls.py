# -*- coding: utf-8 -*-
"""sshostmgt URL Configuration
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib import staticfiles
from sshostmgt import views

admin.autodiscover()

urlpatterns = [
    url(r'^$', views.get_all_hosts),
    url(r'^hosts$', views.get_all_hosts),
    url(r'^hosts/(?P<hostname>[a-zA-Z0-9_\-]+)/info$', views.get_host_info),
    url(r'^hosts/(?P<hostname>[a-zA-Z0-9_\-]+)/reboot$', views.reboot),
    url(r'^hosts/(?P<hostname>[a-zA-Z0-9_\-]+)/shutdown$', views.shutdown),
    url(r'^hosts/(?P<hostname>[a-zA-Z0-9_\-]+)/wakeup$', views.wakeup),
    url(r'^hosts/(?P<hostname>[a-zA-Z0-9_\-]+)/powerstatus$', views.get_power_status)
]
