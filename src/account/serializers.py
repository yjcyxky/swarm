# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

from django.contrib.auth.models import User
from rest_framework import serializers
import logging

logger = logging.getLogger(__name__)

class UserSerializer(serializers.HyperlinkedModelSerializer):
    password = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'email', 'is_staff', 'is_active',
                  'password', 'date_joined', 'last_login')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data, **kwargs):
        instance.email = validated_data.get('email', instance.email)
        instance.is_staff = validated_data.get('is_staff', instance.is_staff)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        if validated_data.get('password') is not None:
            instance.set_password(validated_data['password'])

        if kwargs.get('password') is not None:
            # 重置密码为用户名
            instance.set_password(kwargs.get('password'))
            logger.debug("UserSerializer@update@reset_password@%s" % kwargs.get('password'))

        logger.debug("UserSerializer@update@validated_data@%s" % validated_data)
        instance.save()
        return instance
