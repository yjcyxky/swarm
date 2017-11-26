from django.contrib.auth.models import User
from rest_framework import serializers, viewsets
import logging

logger = logging.getLogger(__name__)

class UserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff', 'is_active', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.is_staff = validated_data.get('is_staff', instance.is_staff)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.set_password(validated_data.get('password', instance.password))
        instance.save()
        return instance

class PasswordSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields = ('url', 'password', 'email', 'is_active')
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, user, password):
        user.set_password(password)
        user.save()
        return user
