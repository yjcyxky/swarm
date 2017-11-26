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
from sshostmgt import views

urlpatterns = [
    url(r'^ipmi$',
        views.IPMIList.as_view(),
        name = "ipmi-list"),
    url(r'^ipmi/(?P<pk>[0-9]+)$',
        views.IPMIDetail.as_view(),
        name = "ipmi-detail"),
]

# urlpatterns = [
#     url(r'^$', views.get_all_hosts),
#     url(r'^hosts$', views.get_all_hosts),
#     url(r'^hosts/(?P<hostname>[a-zA-Z0-9_\-]+)/info$', views.get_host_info),
#     url(r'^hosts/(?P<hostname>[a-zA-Z0-9_\-]+)/reboot$', views.reboot),
#     url(r'^hosts/(?P<hostname>[a-zA-Z0-9_\-]+)/shutdown$', views.shutdown),
#     url(r'^hosts/(?P<hostname>[a-zA-Z0-9_\-]+)/wakeup$', views.wakeup),
#     url(r'^hosts/(?P<hostname>[a-zA-Z0-9_\-]+)/powerstatus$', views.get_power_status)
# ]
