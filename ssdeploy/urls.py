"""ssdeploy URL Configuration

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
from django.contrib import admin
from django.contrib import staticfiles
from ssdeploy import settings
from ssdeploy import views

# admin.autodiscover()

urlpatterns = [
    # url(r'^admin/(.*)$', admin.site.root),
    url(r'^$', views.index),
    url(r'^sscobbler/', include('sscobbler.urls')),
]

# This is only needed when using runserver.
if settings.DEBUG:
    urlpatterns = [
        url(r'^media/(?P<path>.*)$', staticfiles.views.serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        url(r'^static/(?P<path>.*)$', staticfiles.views.serve,
            {'document_root': settings.STATIC_URL, 'show_indexes': True}),] + urlpatterns