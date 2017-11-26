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
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework_jwt.views import verify_jwt_token
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer
from opsweb import views

schema_view = get_schema_view(title='Opsweb APIs', renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer])

urlpatterns = [
    url(r'^api/v1/', include([
        url(r'^docs/', schema_view, name="docs"),
        url(r'^users$',
            views.UserList.as_view(),
            name = "user-list"),
        url(r'^users/(?P<pk>[0-9]+)$',
            views.UserDetail.as_view(),
            name = "user-detail"),
        # For API Documentation
        url(r'^api-auth/',
            include('rest_framework.urls', namespace = 'rest_framework')),
        url(r'^api-token-auth$', obtain_jwt_token),
        url(r'^api-token-refresh$', refresh_jwt_token),
        url(r'^api-token-verify$', verify_jwt_token),

        # # Cobbler
        # url(r'^sscobbler/', include('sscobbler.urls')),
        # # Host Management
        url(r'^sshostmgt/', include('sshostmgt.urls')),
    ])),
]
