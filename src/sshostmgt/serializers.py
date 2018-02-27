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
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator
from sshostmgt.models import (IPMI, Host, Tag, Storage)
from sshostmgt.power_mgmt import get_ipmi_client

logger = logging.getLogger(__name__)

def check_mac(mac):
    MAC_GROUPS = 6
    MAC_DELIMITER = ':'
    MAC_RE = re.compile("([0-9a-f]{2})" +
                        ("\%s([0-9a-f]{2})" % MAC_DELIMITER) * (MAC_GROUPS - 1),
                        flags=re.IGNORECASE)
    match = re.match(MAC_RE, mac)
    if match is None:
        raise serializers.ValidationError("Not a mac address.")

def check_name(name, msg = 'Not a valid name.'):
    RE = re.compile("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-\_]*[A-Za-z0-9])$")
    match = re.match(RE, name)
    if match is None:
        raise serializers.ValidationError(msg)

def check_hostname(hostname):
    check_name(hostname, 'Not a valid host name.')

def check_tag_name(tag_name):
    check_name(tag_name, 'Not a valid tag name.')

def check_storage_name(storage_name):
    check_name(storage_name, 'Not a valid storage name.')

def check_path(path):
    RE = re.compile("^/[a-zA-Z0-9\-_/]+$")
    match = re.match(RE, path)
    if match is None:
        raise serializers.ValidationError('Not a valid path, you must specify the path as an unix absolute path')

def check_label_color(color_name):
    COLOR_RE = re.compile('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
    RegexValidator(COLOR_RE, 'Enter a valid color.', status.HTTP_400_BAD_REQUEST)

class IPMISerializer(serializers.ModelSerializer):
    ipmi_passwd = serializers.CharField()
    last_update_time = serializers.DateTimeField()
    first_add_time = serializers.DateTimeField()
    ipmi_addr = serializers.IPAddressField()
    ipmi_mac = serializers.CharField(min_length=17, max_length=17)

    class Meta:
        model = IPMI
        fields = ('ipmi_uuid', 'ipmi_mac', 'ipmi_addr', 'ipmi_username', 'ipmi_passwd',
                  'power_state', 'last_update_time', 'first_add_time', 'ipmi_desc')
        # extra_kwargs = {'ipmi_passwd': {'write_only': True}}
        lookup_field = 'ipmi_uuid'

        extra_kwargs = {
            'ipmi_uuid': {
                'validators': []
            },
            'ipmi_mac': {
                'validators': [check_mac]
            },
            'ipmi_addr': {
                'validators': []
            }
        }

    def custome_validate_ipmi_mac(self, value):
        if IPMI.objects.filter(ipmi_mac=value):
            raise serializers.ValidationError("This field must be unique.")

    def custome_validate_ipmi_addr(self, value):
        if IPMI.objects.filter(ipmi_addr=value):
            raise serializers.ValidationError("This field must be unique.")

    def custome_validate_ipmi_uuid(self, value):
        if IPMI.objects.filter(ipmi_uuid=value):
            raise serializers.ValidationError("This field must be unique.")

    def create(self, validated_data):
        # save将调用create创建用户
        self.custome_validate_ipmi_mac(validated_data.get('ipmi_mac'))
        self.custome_validate_ipmi_addr(validated_data.get('ipmi_addr'))
        self.custome_validate_ipmi_uuid(validated_data.get('ipmi_uuid'))
        power_state = validated_data.get('power_state', 'POWER_OFF').upper()
        if validated_data.get('power_state'):
            validated_data.pop('power_state')
        ipmi = IPMI.objects.create(power_state = power_state, **validated_data)
        ipmi.save()
        return ipmi

    def update(self, instance, validated_data):
        instance.ipmi_username = validated_data.get('ipmi_username', instance.ipmi_username)
        instance.ipmi_passwd = validated_data.get('ipmi_passwd', instance.ipmi_passwd)
        instance.last_update_time = validated_data.get('last_update_time', instance.last_update_time)
        instance.power_state = validated_data.get('power_state', instance.power_state).upper()
        instance.save()
        return instance

    def update_power_state(self, instance, power_state):
        # Reset数据库记录，具体状态由power_monitor更新
        original_state = instance.power_state
        instance.power_state = 'CHANGED'
        instance.last_update_time = datetime.datetime.now()
        ipmi_username = instance.ipmi_username
        ipmi_passwd = instance.ipmi_passwd
        ipmi_addr = instance.ipmi_addr
        ipmi_client = get_ipmi_client(ipmi_username, ipmi_passwd, ipmi_addr)
        if ipmi_client:
            try:
                ipmi_client.set_power_state(target_state = power_state.upper())
            except:
                # TODO: 修改Response Status
                # 未修改成功则返回原记录
                instance.power_state = original_state
        instance.save()
        return instance

    def validate(self, data):
        """
        Check that the first_add_time is before the last_update_time.
        """
        if data.get('first_add_time') and data.get('last_update_time'):
            if data.get('first_add_time') > data.get('last_update_time'):
                raise serializers.ValidationError("last_update_time must occur after first_add_time.")
        return data

    def validate_power_state(self, value):
        """
        Check that the power state is in POWER_STATE dictionary.
        """
        if value.upper() not in ("POWER_ON", "POWER_OFF", "REBOOT", "UNKNOWN"):
            raise serializers.ValidationError("The power state must be one of POWER_ON, POWER_OFF, REBOOT, and UNKNOWN")
        return value

class TagSerializer(serializers.ModelSerializer):
    tag_name = serializers.CharField(validators = [check_tag_name, UniqueValidator(queryset=Tag.objects.all())])
    label_color = serializers.CharField(validators = [check_label_color], default='#23d7bc')
    common_used = serializers.BooleanField(default=False)

    class Meta:
        model = Tag
        fields = ('tag_uuid', 'tag_desc', 'tag_name', 'label_color', 'common_used', 'tag_name_alias')
        lookup_field = 'tag_uuid'

    def create(self, validated_data):
        tag_name = validated_data.get('tag_name')
        if validated_data.get('tag_name_alias') is None:
            tag = Tag.objects.create(tag_name_alias = tag_name, **validated_data)
        else:
            tag = Tag.objects.create(**validated_data)
        tag.save()
        return tag

    def update(self, instance, validated_data):
        instance.tag_name_alias = validated_data.get('tag_name_alias', instance.tag_name_alias)
        instance.common_used = validated_data.get('common_used', instance.common_used)
        instance.label_color = validated_data.get('label_color', instance.label_color)
        instance.save()
        return instance

class HostListSerializer(serializers.HyperlinkedModelSerializer):
    ipmi = IPMISerializer(read_only = True)
    host_uuid = serializers.UUIDField(format = 'hex_verbose')
    mgmt_ip_addr = serializers.IPAddressField()
    mgmt_mac = serializers.CharField(min_length = 17, max_length = 17,
                                     validators = [check_mac, UniqueValidator(queryset=Host.objects.all())])
    hostname = serializers.CharField(validators = [check_hostname], max_length = 64)
    tags = TagSerializer(many = True, read_only = True)

    class Meta:
        model = Host
        fields = ('host_uuid', 'host_desc', 'mgmt_ip_addr', 'mgmt_mac',
                  'hostname', 'ipmi', 'tags')
        lookup_field = 'host_uuid'

class HostSerializer(serializers.HyperlinkedModelSerializer):
    ipmi = IPMISerializer()
    host_uuid = serializers.UUIDField(format = 'hex_verbose')
    mgmt_ip_addr = serializers.IPAddressField()
    hostname = serializers.CharField(validators = [check_hostname], max_length = 64)
    tags = TagSerializer(many=True, read_only=True)
    tags_uuid = serializers.PrimaryKeyRelatedField(many=True,
                                                   queryset = Tag.objects.all(),
                                                   pk_field = serializers.UUIDField(format='hex_verbose'),
                                                   source='tags')

    class Meta:
        model = Host
        fields = ('host_uuid', 'host_desc', 'mgmt_ip_addr', 'hostname', 'ipmi',
                  'tags', 'tags_uuid', 'mgmt_mac')
        lookup_field = 'host_uuid'

    def create(self, validated_data):
        ipmi_data = validated_data.pop('ipmi')
        tags = validated_data.pop('tags')
        ipmi = IPMI.objects.create(**ipmi_data)
        host = Host.objects.create(ipmi=ipmi, **validated_data)
        host.save()
        host.tags.add(*tags)
        return host

    def update(self, instance, validated_data):
        instance.cluster_uuid = validated_data.get('cluster_uuid', instance.cluster_uuid)
        instance.host_desc = validated_data.get('host_desc', instance.host_desc)
        instance.hostname = validated_data.get('hostname', instance.hostname)
        instance.mgmt_ip_addr = validated_data.get('mgmt_ip_addr', instance.mgmt_ip_addr)
        instance.mgmt_mac = validated_data.get('mgmt_mac', instance.mgmt_mac)
        ipmi_data = validated_data.get('ipmi')
        ipmi = IPMI.objects.filter(ipmi_uuid=ipmi_data.get('ipmi_uuid'))
        if ipmi_data and ipmi:
            ipmi.update(**ipmi_data)
        elif ipmi_data and not ipmi:
            serializer = IPMISerializer(data=ipmi_data)
            if serializer.is_valid():
                ipmi = serializer.create(serializer.validated_data)
                instance.ipmi = ipmi

        tags = validated_data.get('tags', None)
        instance.save()
        if tags:
            instance.tags.clear()
            instance.tags.add(*tags)
        return instance

class BIOSSerializer(serializers.ModelSerializer):
    pass

class NetworkSerializer(serializers.ModelSerializer):
    pass

class CPUSerializer(serializers.ModelSerializer):
    pass

class StorageSerializer(serializers.HyperlinkedModelSerializer):
    storage_name = serializers.CharField(validators = [check_storage_name, UniqueValidator(queryset=Storage.objects.all())])
    host = serializers.PrimaryKeyRelatedField(queryset = Host.objects.all(),
                                              pk_field = serializers.UUIDField(format='hex_verbose'))
    storage_path = serializers.CharField(validators = [check_path, UniqueValidator(queryset = Storage.objects.all())])

    class Meta:
        model = Storage
        fields = ('storage_uuid', 'storage_desc', 'storage_name', 'storage_path',
                  'total_size', 'remaining_size', 'host', 'username', 'groupname')
        lookup_field = 'storage_uuid'

    def create(self, validated_data):
        storage = Storage.objects.create(**validated_data)
        storage.save()
        return storage

    def update(self, instance, validated_data):
        instance.storage_desc = validated_data.get('storage_desc', instance.storage_desc)
        instance.username = validated_data.get('username', instance.username)
        instance.groupname = validated_data.get('groupname', instance.groupname)
        instance.remaining_size = validated_data.get('remaining_size', instance.remaining_size)
        instance.total_size = validated_data.get('total_size', instance.total_size)
        instance.save()
        return instance

    def validate(self, data):
        """
        Check that the total_size is greater or equal than the remaining_size.
        """
        if data.get('total_size') and data.get('remaining_size'):
            if data.get('remaining_size') > data.get('total_size'):
                raise serializer.ValidationError("remaining_size must be equal or less than total_size.")
        return data

class SystemSerializer(serializers.ModelSerializer):
    pass

class RAIDSerializer(serializers.ModelSerializer):
    pass
