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

    def get_notifi_type_str(self, notification_type):
        if notification_type == 0:
            return 'Host notification'
        elif notification_type == 1:
            return 'Service notification'
        else:
            return notification_type

    def get_escalated_str(self, escalated):
        if escalated == 0:
            return 'NOT escalated'
        elif escalated == 1:
            return 'Escalated'
        else:
            return escalated

    def get_notifi_reason_str(self, notification_reason):
        reason_dict = {
            '0': 'Normal notification',
            '1': 'Problem acknowledgement',
            '2': 'Flapping started',
            '3': 'Flapping stopped',
            '4': 'Flapping was disabled',
            '5': 'Downtime started',
            '6': 'Downtime ended',
            '7': 'Downtime was cancelled',
            '99': 'Custom notification'
        }
        return reason_dict.get(str(notification_reason), 'Unknown reason')

    def get_state_str(self, notifi_type, state):
        host_state_dict = {
            '0': 'UP',
            '1': 'DOWN',
            '2': 'CRITICAL'
        }

        service_state_dict = {
            '0': 'OK',
            '1': 'WARNING',
            '2': 'CRITICAL',
            '3': 'UNKNOWN'
        }
        if notifi_type == 0:
            return host_state_dict.get(str(state))
        elif notifi_type == 1:
            return service_state_dict.get(str(state))

    def to_representation(self, instance):
        instance = instance.__dict__
        notifi_type = instance.get('notification_type')
        notifi_reason = instance.get('notification_reason')
        return {
            'instance': instance.get('instance'),
            'object': instance.get('object'),
            'notification_id': instance.get('notification_id'),
            'notification_type': self.get_notifi_type_str(notifi_type),
            'notification_reason': self.get_notifi_reason_str(notifi_reason),
            'start_time': instance.get('start_time'),
            'start_time_usec': instance.get('start_time_usec'),
            'end_time': instance.get('end_time'),
            'end_time_usec': instance.get('end_time_usec'),
            'state': self.get_state_str(notifi_type, instance.get('state')),
            'output': instance.get('output'),
            'long_output': instance.get('long_output'),
            'escalated': self.get_escalated_str(instance.get('escalated')),
            'contacts_notified': instance.get('contacts_notified'),
            'checked': instance.get('checked'),
            'checked_time': instance.get('checked_time')
        }

    class Meta:
        model = Notifications
        fields = ('instance', 'object', 'notification_id',
                  'notification_type', 'notification_reason', 'start_time',
                  'start_time_usec', 'end_time', 'end_time_usec', 'state',
                  'output', 'long_output', 'escalated', 'contacts_notified',
                  'checked', 'checked_time')
