# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

from django.conf.urls import url
from account import views

urlpatterns = [
    url(r'^current-user$',
        views.current_user,
        name = "current-user"),
    url(r'^users$',
        views.UserList.as_view(),
        name = "user-list"),
    url(r'^users/(?P<pk>[0-9]+)$',
        views.UserDetail.as_view(),
        name = "user-detail"),
]
