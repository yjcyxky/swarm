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
