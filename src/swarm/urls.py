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
from django.contrib.auth import views as auth_views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.generic.base import RedirectView
from swarm import views
from swarm import settings
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="Swarm Management API",
      default_version='v1',
      description="A swagger endpoint for swarm management api.",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="yjcyxky@163.com"),
      license=openapi.License(name="GPLv3 License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # For API Documentation
    url(r'^accounts/login/$', auth_views.LoginView, name='login'),
    url(r'^api/v1/', include([
        url(r'^apis/(?P<api_name>[a-zA-Z0-9]+)$',
            views.APIDetail.as_view(),
            name="api-list"),

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

    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', views.serve),
    ]
