# -*- coding: utf-8 -*-
"""sshostmgt URL Configuration
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib import staticfiles
from sshostmgt import views

admin.autodiscover()

urlpatterns = [
    url(r'^host/(?P<hostname>[a-zA-Z0-9_\-]+)/info$', views.get_host_info),
    url(r'^host/(?P<hostname>[a-zA-Z0-9_\-]+)/reboot$', views.reboot),
    url(r'^host/(?P<hostname>[a-zA-Z0-9_\-]+)/shutdown$', views.shutdown),
    url(r'^host/(?P<hostname>[a-zA-Z0-9_\-]+)/wakeup$', views.wakeup),
    url(r'^host/(?P<hostname>[a-zA-Z0-9_\-]+)/powerstatus$', views.get_power_status)
    url(r'^host/(?P<hostname>[a-zA-Z0-9_\-]+)/get_ipmi_info$', views.get_ipmi_info)
    url(r'^host/(?P<hostname>[a-zA-Z0-9_\-]+)/set_ipmi_info$', views.set_ipmi_info)
]