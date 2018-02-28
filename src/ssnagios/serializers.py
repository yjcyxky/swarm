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
from ssnagios.models import Instances, Objects, Notifications, Hosts
from django.utils import timezone

logger = logging.getLogger(__name__)


class HostsSerializer(serializers.ModelSerializer):
    def get_object_model(self, value):
        return Objects.objects.get(object_id=value)

    def to_representation(self, instance):
        nagios_instance = Instances.objects.get(instance_id=instance.instance_id)
        instance_dict = instance.__dict__
        host_object_id = instance_dict.get('host_object_id')
        check_command_object_id = instance_dict.get('check_command_object_id')
        return {
            'host_id': instance_dict.get('host_id'),
            'instance': InstancesSerializer(nagios_instance).data,
            'config_type': instance_dict.get('config_type'),
            'host_object': ObjectsSerializer(self.get_object_model(host_object_id)).data,
            'alias': instance_dict.get('alias'),
            'display_name': instance_dict.get('display_name'),
            'address': instance_dict.get('address'),
            'check_command_object': ObjectsSerializer(self.get_object_model(check_command_object_id)).data,
            'check_command_args': instance_dict.get('check_command_args'),
        }

    class Meta:
        model = Hosts
        fields = '__all__'


class InstancesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Instances
        fields = ('instance_id', 'instance_name', 'instance_description')


class ObjectsSerializer(serializers.ModelSerializer):
    def get_objecttype_str(self, objecttype_id):
        objecttype_dict = {
            '1': 'Host',
            '2': 'Service',
            '3': 'Host group',
            '4': 'Service group',
            '5': 'Host escalation',
            '6': 'Service escalation',
            '7': 'Host dependency',
            '8': 'Service dependency',
            '9': 'Timeperiod',
            '10': 'Contact',
            '11': 'Contact group',
            '12': 'Command',
            '13': 'Extended host info (deprecated)',
            '14': 'Extended service info'
        }
        return objecttype_dict.get(str(objecttype_id), 'Unknown objecttype')

    def get_is_active_str(self, is_active):
        if is_active == 0:
            return 'Inactive'
        elif is_active == 1:
            return 'Active'
        else:
            return 'Unknown'

    def to_representation(self, instance):
        instance = instance.__dict__
        objecttype_id = instance.get('objecttype_id')
        return {
            'object_id': instance.get('object_id'),
            'instance_id': instance.get('instance_id'),
            'objecttype_id': self.get_objecttype_str(objecttype_id),
            'name1': instance.get('name1'),
            'name2': instance.get('name2'),
            'is_active': self.get_is_active_str(instance.get('is_active'))
        }

    class Meta:
        model = Objects
        fields = '__all__'


class NotificationsSerializer(serializers.ModelSerializer):
    instance = InstancesSerializer()
    object = ObjectsSerializer()
    checked = serializers.BooleanField()
    checked_time = serializers.DateTimeField()

    def get_checked_str(self, checked):
        if not checked:
            return 'UNREAD'
        elif checked:
            return 'READ'
        else:
            return 'UNKNOWN'

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
        nagios_instance = Instances.objects.get(instance_id=instance.instance_id)
        nagios_object = Objects.objects.get(object_id=instance.object_id)
        instance = instance.__dict__
        notifi_type = instance.get('notification_type')
        notifi_reason = instance.get('notification_reason')
        return {
            'instance': InstancesSerializer(nagios_instance).data,
            'object': ObjectsSerializer(nagios_object).data,
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
            'checked': self.get_checked_str(instance.get('checked')),
            'checked_time': instance.get('checked_time')
        }

    def update(self, instance, validated_data):
        checked = validated_data.get('checked')
        instance.checked = bool(checked)
        instance.checked_time = timezone.now()
        instance.save()

    class Meta:
        model = Notifications
        fields = ('instance', 'object', 'notification_id',
                  'notification_type', 'notification_reason', 'start_time',
                  'start_time_usec', 'end_time', 'end_time_usec', 'state',
                  'output', 'long_output', 'escalated', 'contacts_notified',
                  'checked', 'checked_time')
