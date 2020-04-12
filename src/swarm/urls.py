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
from rest_framework_jwt.views import (obtain_jwt_token, refresh_jwt_token,
                                      verify_jwt_token)
from django.contrib import admin
from rest_framework import permissions
from swarm import views
from swarm import settings


urlpatterns = [
    # For API Documentation
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^version$', views.get_version, name='version'),
    url(r'^api/v1/', include([
        # API Token
        url(r'^api-token-auth$', obtain_jwt_token),
        url(r'^api-token-refresh$', refresh_jwt_token),
        url(r'^api-token-verify$', verify_jwt_token),

        # Account System
        url(r'^accounts/', include('account.urls')),

        # Cobbler
        url(r'^sscobbler/', include('sscobbler.urls')),

        # Host Management
        url(r'^sshostmgt/', include('sshostmgt.urls')),
        url(r'^sscluster/', include('sscluster.urls')),
        url(r'^sscobweb/', include('sscobweb.urls')),
        url(r'^grafana/', include('grafana.urls')),
        url(r'^agent-state', views.agent_state, name='agent_state'),

        url(r'^.*$', views.custom404, name='custom404')
    ])),
    url(r'^.*$', views.custom404, name="custom404")
]

if settings.DEBUG:
    from django.contrib.staticfiles import views
    from django.urls import re_path
    # If you want to collect static files in production mode,
    # you need to use django.contrib.staticfiles
    # Do Not need to use static files in the restful project.
    from django.conf.urls.static import static
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns = [
        re_path(r'^static/(?P<path>.*)$', views.serve),
    ] + urlpatterns
