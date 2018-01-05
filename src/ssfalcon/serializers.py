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
from django.core.validators import RegexValidator

logger = logging.getLogger(__name__)

class TimestampField(serializers.Field):
    def to_representation(self, value):
        return int(time.mktime(value.timetuple()))

    def to_internal_value(self, value):
        return value

class AggregatorSerializer(serializers.Serializer):
    tags = serializers.CharField(allow_blank = True, trim_whitespace = True)
    step = serializers.IntegerField()
    numerator = serializers.CharField(trim_whitespace = True)
    metric = serializers.CharField(trim_whitespace = True)
    hostgroup_id = serializers.IntegerField(required = False)
    endpoint = serializers.CharField(trim_whitespace = True)
    denominator = serializers.CharField(trim_whitespace = True)
    id = serializers.IntegerField(allow_null = True, required = False)


class EventSerializer(serializers.Serializer):
    startTime = TimestampField(required = False)
    endTime = TimestampField(required = False)
    status = serializers.CharField(trim_whitespace = True, required = False)
    process_status = serializers.CharField(trim_whitespace = True, required = False)
    limit = serializers.IntegerField(required = False)
    event_id = serializers.CharField(trim_whitespace = True, required = False)
    note = serializers.CharField(trim_whitespace = True, required = False)

    def validate(self, data):
        """
        Check that the first_add_time is before the last_update_time.
        """
        if data.get('startTime') and data.get('endTime'):
            if data.get('startTime') > data.get('endTime'):
                raise serializer.ValidationError("endTime must occur after startTime.")
        return data
