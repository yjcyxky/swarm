# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import logging
from django.db import models

logger = logging.getLogger(__name__)

class Panel(models.Model):
    PANEL_TYPE = (
        ('BarChart', 'BarChart'),
        ('Histogram', 'Histogram'),
        ('LineChart', 'LineChart'),
        ('Gauge', 'Gauge'),
        ('Table', 'Table'),
        ('Heatmap', 'Heatmap'),
        ('PieChart', 'PieChart'),
        ('RingChart', 'RingChart'),
        ('ScatterChart', 'ScatterChart')
    )

    panel_uuid = models.CharField(max_length=36, primary_key=True)
    db_name = models.CharField(max_length=32, help_text='Database name in influxDB.')
    query_str = models.TextField(help_text='Query string in querying language.')
    panel_type = models.CharField(max_length=32, choices=PANEL_TYPE, default='LineChart', help_text='Chart type.')
    refresh = models.BooleanField(default=True, help_text='Return True if you want to refresh panel.')
    refresh_interval = models.PositiveIntegerField(help_text='Refresh Interval (default: second).')
    tag_name = models.CharField(max_length=32, null=True, blank=True)
    title = models.CharField(max_length=255, help_text='Panel name.')
    created_time = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.panel_uuid

    class Meta:
        ordering = ('created_time',)


class Dashboard(models.Model):
    dashboard_uuid = models.CharField(max_length=36, primary_key=True)
    title = models.CharField(max_length=255, help_text='Dashboard name.')
    dashboard_model = models.TextField(help_text="JSON string for the dashboard.")
    created_time = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.dashboard_uuid

    class Meta:
        ordering = ('created_time',)
