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
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer
from django.contrib.auth import views as auth_views
from opsweb import views

schema_view = get_schema_view(title='Opsweb APIs', renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer])

urlpatterns = [
    # For API Documentation
    url(r'^$', schema_view, name="docs"),
    url(r'^api-auth/',
        include('rest_framework.urls', namespace = 'rest_framework')),
    url(r'^accounts/login/$', auth_views.login, name='login'),
    url(r'^api/v1/', include([
        url(r'^auth/user$',
            views.current_user,
            name = "current-user"),
        url(r'^apis/(?P<api_name>[a-zA-Z0-9]+)$',
            views.APIDetail.as_view(),
            name = "api-list"),
        url(r'^users$',
            views.UserList.as_view(),
            name = "user-list"),
        url(r'^users/(?P<pk>[0-9]+)$',
            views.UserDetail.as_view(),
            name = "user-detail"),

        url(r'^api-token-auth$', obtain_jwt_token),
        url(r'^api-token-refresh$', refresh_jwt_token),
        url(r'^api-token-verify$', verify_jwt_token),

        # # Cobbler
        # url(r'^sscobbler/', include('sscobbler.urls')),
        # # Host Management
        url(r'^sshostmgt/', include('sshostmgt.urls')),
        url(r'^ssfalcon/', include('ssfalcon.urls')),
        url(r'^sscluster/', include('sscluster.urls')),
        url(r'^sscobweb/', include('sscobweb.urls')),
        url(r'^ssadvisor/', include('ssadvisor.urls')),
        url(r'^.*/$', views.custom404)
    ])),
    url(r'^.*/$', views.custom404)
]

import settings
if settings.DEBUG:
    from django.conf.urls.static import static
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
