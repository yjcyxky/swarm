from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
import logging

logger = logging.getLogger(__name__)

class HostSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff', 'is_active', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # save将调用create创建用户
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class IPMISerializer(serializers.ModelSerializer):
    pass

class BIOSSerializer(serializers.ModelSerializer):
    pass

class NetworkSerializer(serializers.ModelSerializer):
    pass

class CPUSerializer(serializers.ModelSerializer):
    pass

class Storage(serializer.ModelSerializer):
    pass

class System(serializer.ModelSerializer):
    pass

class RAID(serializer.ModelSerializer):
    pass
