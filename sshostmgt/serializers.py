import logging
import re
import datetime
from rest_framework import serializers
from rest_framework import status
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator
from sshostmgt.models import (IPMI, Host, Tag)
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

def check_hostname(hostname):
    HOST_RE = re.compile("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-\_]*[A-Za-z0-9])$")
    match = re.match(HOST_RE, hostname)
    if match is None:
        raise serializers.ValidationError("Not a valid host name.")

def check_tag_name(tag_name):
    TAG_RE = re.compile("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-\_]*[A-Za-z0-9])$")
    match = re.match(TAG_RE, tag_name)
    if match is None:
        raise serializers.ValidationError("Not a valid tag name.")

def check_label_color(color_name):
    COLOR_RE = re.compile('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
    RegexValidator(COLOR_RE, 'Enter a valid color.', status.HTTP_400_BAD_REQUEST)

class IPMISerializer(serializers.ModelSerializer):
    ipmi_passwd = serializers.CharField(write_only = True)
    last_update_time = serializers.DateTimeField()
    first_add_time = serializers.DateTimeField()
    ipmi_addr = serializers.IPAddressField(validators = [UniqueValidator(queryset=IPMI.objects.all())])
    ipmi_mac = serializers.CharField(min_length = 17, max_length = 17,
                                     validators = [check_mac, UniqueValidator(queryset=IPMI.objects.all())])

    class Meta:
        model = IPMI
        fields = ('ipmi_uuid', 'ipmi_mac', 'ipmi_addr', 'ipmi_username', 'ipmi_passwd',
                  'power_state', 'last_update_time', 'first_add_time')
        extra_kwargs = {'ipmi_passwd': {'write_only': True}}
        lookup_field = 'ipmi_uuid'

    def create(self, validated_data):
        # save将调用create创建用户
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
                raise serializer.ValidationError("last_update_time must occur after first_add_time.")
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
    label_color = serializers.CharField(validators = [check_label_color])

    class Meta:
        model = Tag
        fields = ('tag_uuid', 'tag_name', 'label_color', 'common_used', 'tag_name_alias')
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

class HostSerializer(serializers.HyperlinkedModelSerializer):
    ipmi = serializers.PrimaryKeyRelatedField(queryset = IPMI.objects.all(),
                                              pk_field = serializers.UUIDField(format='hex_verbose'))
    host_uuid = serializers.UUIDField(format = 'hex_verbose')
    mgmt_ip_addr = serializers.IPAddressField()
    hostname = serializers.CharField(validators = [check_hostname], max_length = 64)
    # tags = TagSerializer(many = True, read_only = True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset = Tag.objects.all(),
                                              pk_field = serializers.UUIDField(format='hex_verbose'))

    class Meta:
        model = Host
        fields = ('host_uuid', 'mgmt_ip_addr', 'hostname', 'ipmi', 'tags')
        lookup_field = 'host_uuid'

    def create(self, validated_data):
        print(dir(validated_data))
        print(validated_data)
        ipmi = validated_data.pop('ipmi')
        host = Host.objects.create(ipmi = ipmi, **validated_data)
        host.save()
        tags = validated_data.pop('tags')
        host.tags.add(*tags)
        return host

class BIOSSerializer(serializers.ModelSerializer):
    pass

class NetworkSerializer(serializers.ModelSerializer):
    pass

class CPUSerializer(serializers.ModelSerializer):
    pass

class Storage(serializers.ModelSerializer):
    pass

class System(serializers.ModelSerializer):
    pass

class RAID(serializers.ModelSerializer):
    pass
