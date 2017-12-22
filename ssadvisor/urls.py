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
from ssadvisor import views

urlpatterns = [
    url(r'^patients$',
        views.PatientList.as_view(),
        name = 'patient-list'),
    url(r'^patients/(?P<patient_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.PatientDetail.as_view(),
        name = 'patient-detail'),
    url(r'^tasks$',
        views.TaskList.as_view(),
        name = 'task-list'),
    url(r'^tasks/(?P<task_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.TaskDetail.as_view(),
        name = 'task-detail'),
    url(r'^files/(?P<file_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.FileDetail.as_view(),
        name = 'file-detail'),
    url(r'^files$',
        views.FileList.as_view(),
        name = 'file-list'),
    url(r'^reports/(?P<report_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.ReportDetail.as_view(),
        name = 'report-detail'),
    url(r'^reports$',
        views.ReportList.as_view(),
        name = 'report-list'),
    url(r'^settings/(?P<setting_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.SettingDetail.as_view(),
        name = 'setting-detail'),
    url(r'^settings$',
        views.SettingList.as_view(),
        name = 'setting-list'),
]
