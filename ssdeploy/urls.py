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
from django.conf.urls import url
from django.contrib import admin
from django.contrib import staticfiles
import settings
import views

admin.autodiscover()

urlpatterns = [
    url(r'^$', views.index),

    url(r'^setting/list$', views.setting_list),
    url(r'^setting/edit/(?P<setting_name>.+)$', views.setting_edit),
    url(r'^setting/save$', views.setting_save),

    url(r'^aifile/list(/(?P<page>\d+))?$', views.aifile_list),
    url(r'^aifile/edit$', views.aifile_edit, {'editmode': 'new'}),
    url(r'^aifile/edit/file:(?P<aifile_name>.+)$', views.aifile_edit, {'editmode': 'edit'}),
    url(r'^aifile/save$', views.aifile_save),

    url(r'^snippet/list(/(?P<page>\d+))?$', views.snippet_list),
    url(r'^snippet/edit$', views.snippet_edit, {'editmode': 'new'}),
    url(r'^snippet/edit/file:(?P<snippet_name>.+)$', views.snippet_edit, {'editmode': 'edit'}),
    url(r'^snippet/save$', views.snippet_save),

    url(r'^(?P<what>\w+)/list(/(?P<page>\d+))?', views.genlist),
    url(r'^(?P<what>\w+)/modifylist/(?P<pref>[!\w]+)/(?P<value>.+)$', views.modify_list),
    url(r'^(?P<what>\w+)/edit/(?P<obj_name>.+)$', views.generic_edit, {'editmode': 'edit'}),
    url(r'^(?P<what>\w+)/edit$', views.generic_edit, {'editmode': 'new'}),

    url(r'^(?P<what>\w+)/rename/(?P<obj_name>.+)/(?P<obj_newname>.+)$', views.generic_rename),
    url(r'^(?P<what>\w+)/copy/(?P<obj_name>.+)/(?P<obj_newname>.+)$', views.generic_copy),
    url(r'^(?P<what>\w+)/delete/(?P<obj_name>.+)$', views.generic_delete),

    url(r'^(?P<what>\w+)/multi/(?P<multi_mode>.+)/(?P<multi_arg>.+)$', views.generic_domulti),
    url(r'^utils/random_mac$', views.random_mac),
    url(r'^utils/random_mac/virttype/(?P<virttype>.+)$', views.random_mac),
    url(r'^events$', views.events),
    url(r'^eventlog/(?P<event>.+)$', views.eventlog),
    url(r'^task_created$', views.task_created),
    url(r'^sync$', views.sync),
    url(r'^reposync$', views.reposync),
    url(r'^replicate$', views.replicate),
    url(r'^hardlink', views.hardlink),
    url(r'^(?P<what>\w+)/save$', views.generic_save),
    url(r'^import/prompt$', views.import_prompt),
    url(r'^import/run$', views.import_run),
    url(r'^buildiso$', views.buildiso),
    url(r'^check$', views.check),

    url(r'^login$', views.login),
    url(r'^do_login$', views.do_login),
    url(r'^logout$', views.do_logout),
]

# This is only needed when using runserver.
if settings.DEBUG:
    urlpatterns = [
        url(r'^media/(?P<path>.*)$', staticfiles.views.serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        url(r'^static/(?P<path>.*)$', staticfiles.views.serve,
            {'document_root': settings.STATIC_URL, 'show_indexes': True}),] + urlpatterns