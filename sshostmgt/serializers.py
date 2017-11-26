import logging
import re
from rest_framework import serializers
from sshostmgt.models import (IPMI, Host, Tag)

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

class IPMISerializer(serializers.ModelSerializer):
    ipmi_passwd = serializers.CharField(write_only = True)
    last_update_time = serializers.DateTimeField()
    first_add_time = serializers.DateTimeField()
    ipmi_addr = serializers.IPAddressField()
    ipmi_mac = serializers.CharField(min_length = 17, max_length = 17, validators = [check_mac])

    class Meta:
        model = IPMI
        fields = ('ipmi_mac', 'ipmi_addr', 'ipmi_username', 'ipmi_passwd',
                  'power_state', 'last_update_time', 'first_add_time')
        extra_kwargs = {'ipmi_passwd': {'write_only': True}}

    def create(self, validated_data):
        # save将调用create创建用户
        ipmi = super(IPMISerializer, self).create(validated_data)
        ipmi.set_password(validated_data['ipmi_passwd'])
        ipmi.save()
        return ipmi

    def update(self, instance, validated_data):
        instance.ipmi_username = validated_data.get('ipmi_username', instance.ipmi_username)
        instance.ipmi_passwd = validated_data.get('ipmi_passwd', instance.ipmi_passwd)
        instance.last_update_time = validated_data.get('last_update_time', instance.last_update_time)
        instance.power_state = validated_data.get('power_state', instance.power_state)
        instance.save()
        return instance

    def validate(self, data):
        """
        Check that the first_add_time is before the last_update_time.
        """
        if data['first_add_time'] > data['last_update_time']:
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
    tag_name = serializers.CharField(validators = [check_tag_name])

    class Meta:
        model = Tag
        fields = ('id', 'tag_name')

class HostSerializer(serializers.HyperlinkedModelSerializer):
    ipmi = IPMISerializer()
    host_uuid = serializers.UUIDField(format = 'hex_verbose')
    ip_addr = serializers.IPAddressField()
    hostname = serializers.CharField(validators = [check_hostname], max_length = 64)
    tags = TagSerializer(many = True, read_only = True)

    class Meta:
        model = Host
        fields = ('host_uuid', 'ip_addr', 'hostname', 'ipmi', 'tags')

    def create(self, validated_data):
        ipmi_data = validated_data.pop('ipmi')
        tags_data = validated_data.pop('tags')
        host = Host.objects.create(**validated_data)
        IPMI.objects.create(ipmi = ipmi, **ipmi_data)
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
