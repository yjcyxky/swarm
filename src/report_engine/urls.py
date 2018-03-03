# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

from django.conf.urls import url
from report_engine import views

urlpatterns = [
    url(r'^reports/metadata$',
        views.ReportList.as_view(),
        name="report-list"),
    url(r'^reports/metadata/(?P<report_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.ReportDetail.as_view(),
        name="report-detail"),
    # 创建指定Report的新版本或者罗列指定Report的所有版本
    url(r'^reports/(?P<report_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.RootNodeList.as_view(),
        name="rootnode-list"),
    # 提供指定版本Report操作接口
    url(r'^reports/(?P<report_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<version_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
        views.RootNodeDetail.as_view(),
        name="rootnode-detail"),
    # 提供用户操作单个Section节点的接口；若需要操作指定版本的Report，则通过Parameters指定，否则默认为最新版Report
    # url(r'^reports/(?P<report_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<section_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
    #     views.SectionNodeDetail.as_view(),
    #     name = "section-node-detail"),
    # 提供用户操作单个内容节点的接口；若需要操作指定版本的Report，则通过Parameters指定，否则默认为最新版Report
    # url(r'^reports/(?P<report_uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/(?P<content_type>[a-zA-Z]+)/(?P<uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$',
    #     views.ContentNodeDetail.as_view(),
    #     name = "content-node-detail"),
]
