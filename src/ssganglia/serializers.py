# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import logging
import time
from rest_framework import serializers
from ssganglia.models import RRDConfigModel

logger = logging.getLogger(__name__)


class TimestampField(serializers.Field):
    def to_representation(self, value):
        return int(time.mktime(value.timetuple()))

    def to_internal_value(self, value):
        return value


class RRDConfigSerializer(serializers.HyperlinkedModelSerializer):
    uuid = serializers.UUIDField(format='hex_verbose')

    class Meta:
        model = RRDConfigModel
        fields = ('uuid', 'filename', 'hostname', 'clustername', 'metric',
                  'metric_type', 'metric_alias')
        lookup_field = 'uuid'

    def create(self, validated_data):
        rrd_config = RRDConfigModel.objects.create(**validated_data)
        rrd_config.save()
        return rrd_config


class RRDSerializer(serializers.Serializer):
    timestamp = serializers.IntegerField(required=True)
    value = serializers.CharField(trim_whitespace=True, max_length=64)
