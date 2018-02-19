# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import logging
from rest_framework import serializers
from ssnagios.models import Instances, Objects, Notifications

logger = logging.getLogger(__name__)


class InstancesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instances
        fields = '__all__'


class ObjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Objects
        fields = '__all__'


class NotificationsSerializer(serializers.ModelSerializer):
    instance = InstancesSerializer()
    object = ObjectsSerializer()
    checked = serializers.BooleanField()
    checked_time = serializers.DateTimeField()

    class Meta:
        model = Notifications
        fields = ('instance', 'object', 'notification_id',
                  'notification_type', 'notification_reason', 'start_time',
                  'start_time_usec', 'end_time', 'end_time_usec', 'state',
                  'output', 'long_output', 'escalated', 'contacts_notified',
                  'checked', 'checked_time')
