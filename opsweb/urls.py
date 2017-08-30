"""opsweb URL Configuration

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
# from django.contrib import admin
from opsweb import settings
from opsweb import views

# admin.autodiscover()

urlpatterns = [
    url(r'^api/v1/', include([
        url(r'^$', views.index, name = "index"),

        # url(r'^admin/', include(admin.site.urls)),
        # Admin for user and group managing
        url(r'^admin/create_user', views.create_user),
        url(r'^admin/update_user', views.update_user),
        url(r'^admin/delete_user', views.delete_user),
        url(r'^admin/change_user_perm', views.change_user_perm),
        url(r'^admin/create_group', views.create_group),
        url(r'^admin/update_group', views.update_group),
        url(r'^admin/delete_group', views.delete_group),
        url(r'^admin/change_group_perm', views.change_group_perm),

        # User Login/Logout
        url(r'^login$', views.login, name = "user_login"),
        url(r'^logout$', views.logout, name = "user_logout"),

        # User Information
        url(r'^users', views.get_users),
        url(r'^users/(?P<username>[a-zA-Z0-9_\-]+)/update', views.update_user),
        url(r'^users/(?P<username>[a-zA-Z0-9_\-]+)', views.get_user),
        url(r'^users/(?P<username>[a-zA-Z0-9_\-]+)/cgpasswd', views.change_passwd),

        # Group Information
        url(r'^groups', views.get_groups),
        url(r'^groups/(?P<groupname>[a-zA-Z0-9_\-]+)/update', views.update_group),
        url(r'^groups/(?P<groupname>[a-zA-Z0-9_\-]+)', views.get_group),

        # Cobbler
        url(r'^sscobbler/', include('sscobbler.urls')),
        # Host Management
        url(r'^sshostmgt/', include('sshostmgt.urls')),
    ])),
]

handler404 = 'opsweb.views.custom404'
