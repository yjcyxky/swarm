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
from rest_framework import routers
from rest_framework_jwt.views import (obtain_jwt_token, refresh_jwt_token, verify_jwt_token)
from rest_framework.schemas import get_schema_view
from swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer
from django.contrib.auth import views as auth_views
from swarm import views

schema_view = get_schema_view(title='Swarm APIs', renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer])

urlpatterns = [
    # For API Documentation
    url(r'^$', schema_view, name="docs"),
    url(r'^api-auth/',
        include('rest_framework.urls', namespace = 'rest_framework')),
    url(r'^accounts/login/$', auth_views.login, name='login'),
    url(r'^api/v1/', include([
        url(r'^apis/(?P<api_name>[a-zA-Z0-9]+)$',
            views.APIDetail.as_view(),
            name = "api-list"),

        ## API Token
        url(r'^api-token-auth$', obtain_jwt_token),
        url(r'^api-token-refresh$', refresh_jwt_token),
        url(r'^api-token-verify$', verify_jwt_token),

        ## Account System
        url(r'^accounts/', include('account.urls')),

        ## Cobbler
        # url(r'^sscobbler/', include('sscobbler.urls')),

        ## Host Management
        url(r'^sshostmgt/', include('sshostmgt.urls')),
        url(r'^ssfalcon/', include('ssfalcon.urls')),
        url(r'^sscluster/', include('sscluster.urls')),
        url(r'^sscobweb/', include('sscobweb.urls')),
        url(r'^ssadvisor/', include('ssadvisor.urls')),
        url(r'^report-engine/', include('report_engine.urls')),
        url(r'^ssganglia/', include('ssganglia.urls')),

        # Flower
        url(r'^flower$',
            views.redirect_flower),
        url(r'^.*/$', views.custom404, name = 'custom404')
    ])),
    url(r'^.*/$', views.custom404, name = "custom404")
]

from swarm import settings
from django.conf import settings
from django.contrib.staticfiles import views
from django.urls import re_path

if settings.DEBUG:
    # If you want to collect static files in production mode, you need to use django.contrib.staticfiles
    # Do Not need to use static files in the restful project.
    from django.conf.urls.static import static
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', views.serve),
    ]
