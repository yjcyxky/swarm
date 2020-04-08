# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import logging
import re
import datetime
from rest_framework import serializers
from rest_framework import status
from grafana.models import (Panel,)

logger = logging.getLogger(__name__)


def check_name(name, msg='Not a valid name.'):
    RE = re.compile("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-\_]*[A-Za-z0-9])$")
    match = re.match(RE, name)
    if match is None:
        raise serializers.ValidationError(msg)


class PanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Panel
        fields = ('panel_uuid', 'db_name', 'query_str', 'panel_type',
                  'refresh', 'refresh_interval', 'tag_name',
                  'created_time')
        lookup_field = 'panel_uuid'

    def create(self, validated_data):
        panel = Panel.objects.create(**validated_data)
        panel.save()
        return panel

    def update(self, instance, validated_data):
        keys = ['db_name', 'query_str', 'panel_type', 'refresh', 'refresh_interval', 'tag_name']
        for key in keys:
            if hasattr(instance, key) and validated_data.get(key):
                setattr(instance, key, validated_data.get(key))

        instance.save()
        return instance
