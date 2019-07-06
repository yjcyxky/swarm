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
import uuid
from django.utils import timezone
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from django.db import transaction
from django.contrib.auth.models import User, AnonymousUser
from lib.rest_framework_recursive.fields import RecursiveField
from report_engine.models import (SectionNode, Version, ReportNode, TitleNode,
                                  InfoNode, ParagraphNode, MediaNode, UrlNode,
                                  ReferenceNode, HeaderNode, FooterNode,
                                  ListNode, TableNode)

logger = logging.getLogger(__name__)


def pop_field(validated_data, field_name):
    if validated_data.get(field_name):
        validated_data.pop(field_name)
    return validated_data


def check_path(path):
    RE = re.compile("^/[a-zA-Z0-9\-_/\.]+$")
    match = re.match(RE, path)
    if match is None:
        raise serializers.ValidationError("Not a valid path, you must specify"
                                          "the path as an unix absolute path")


class TitleNodeSerializer(serializers.ModelSerializer):
    title_uuid = serializers.UUIDField(format='hex_verbose', read_only=True)
    content = serializers.JSONField()

    class Meta:
        model = TitleNode
        fields = ('title_uuid', 'created_time', 'content')


class InfoNodeSerializer(serializers.ModelSerializer):
    info_uuid = serializers.UUIDField(format='hex_verbose', read_only=True)
    content = serializers.JSONField()

    class Meta:
        model = InfoNode
        fields = ('info_uuid', 'created_time', 'content')


class ParagraphNodeSerializer(serializers.ModelSerializer):
    paragraph_uuid = serializers.UUIDField(format='hex_verbose',
                                           read_only=True)
    content = serializers.JSONField()

    class Meta:
        model = ParagraphNode
        fields = ('paragraph_uuid', 'created_time', 'content')


class MediaNodeSerializer(serializers.ModelSerializer):
    media_uuid = serializers.UUIDField(format='hex_verbose', read_only=True)
    content = serializers.JSONField()

    class Meta:
        model = MediaNode
        fields = ('media_uuid', 'created_time', 'content')


class UrlNodeSerializer(serializers.ModelSerializer):
    url_uuid = serializers.UUIDField(format='hex_verbose', read_only=True)
    content = serializers.JSONField()

    class Meta:
        model = UrlNode
        fields = ('url_uuid', 'created_time', 'content')


class ReferenceNodeSerializer(serializers.ModelSerializer):
    reference_uuid = serializers.UUIDField(format='hex_verbose',
                                           read_only=True)
    content = serializers.JSONField()

    class Meta:
        model = ReferenceNode
        fields = ('reference_uuid', 'created_time', 'content')


class HeaderNodeSerializer(serializers.ModelSerializer):
    header_uuid = serializers.UUIDField(format='hex_verbose', read_only=True)
    content = serializers.JSONField()

    class Meta:
        model = HeaderNode
        fields = ('header_uuid', 'created_time', 'content')


class FooterNodeSerializer(serializers.ModelSerializer):
    footer_uuid = serializers.UUIDField(format='hex_verbose', read_only=True)
    content = serializers.JSONField()

    class Meta:
        model = FooterNode
        fields = ('footer_uuid', 'created_time', 'content')


class ListNodeSerializer(serializers.ModelSerializer):
    list_uuid = serializers.UUIDField(format='hex_verbose', read_only=True)
    content = serializers.JSONField()

    class Meta:
        model = ListNode
        fields = ('list_uuid', 'created_time', 'content')


class TableNodeSerializer(serializers.ModelSerializer):
    table_uuid = serializers.UUIDField(format='hex_verbose', read_only=True)
    content = serializers.JSONField()

    class Meta:
        model = TableNode
        fields = ('table_uuid', 'created_time', 'content')


class VersionSerializer(serializers.ModelSerializer):
    version_uuid = serializers.UUIDField(format='hex_verbose')

    class Meta:
        model = Version
        fields = ('version_uuid', 'created_time', 'name_alias')
        extra_kwargs = {
            'version_uuid': {
                "validators": [UniqueValidator(queryset=Version.objects.all())]
            }
        }


class SectionNodeSerializer(serializers.ModelSerializer):
    section_uuid = serializers.UUIDField(format='hex_verbose', required=False,
                                         validators=[UniqueValidator(queryset=SectionNode.objects.all())])
    json_path = serializers.CharField(validators=[check_path, ],
                                      allow_null=True, required=False)
    title_node = TitleNodeSerializer(allow_null=True, required=False)
    info_node = InfoNodeSerializer(allow_null=True, required=False)
    paragraph_node = ParagraphNodeSerializer(allow_null=True, required=False)
    media_node = MediaNodeSerializer(allow_null=True, required=False)
    url_node = UrlNodeSerializer(allow_null=True, required=False)
    reference_node = ReferenceNodeSerializer(allow_null=True, required=False)
    header_node = HeaderNodeSerializer(allow_null=True, required=False)
    footer_node = FooterNodeSerializer(allow_null=True, required=False)
    list_node = ListNodeSerializer(allow_null=True, required=False)
    table_node = TableNodeSerializer(allow_null=True, required=False)
    section_node_set = serializers.ListField(child=RecursiveField(), required=False)
    section_node = RecursiveField(allow_null=True, required=False, many=True, read_only=True)
    report = serializers.PrimaryKeyRelatedField(queryset=ReportNode.objects.all(),
                                                pk_field=serializers.UUIDField(format='hex_verbose'),
                                                required=False)
    version = VersionSerializer(required=False)

    class Meta:
        model = SectionNode
        fields = ('section_uuid', 'section_node_set', 'created_time', 'node_type',
                  'title_node', 'info_node', 'paragraph_node', 'media_node', 'section_node',
                  'url_node', 'reference_node', 'header_node', 'footer_node',
                  'list_node', 'table_node', 'json_path', 'report', 'version')

    def get_field_name(self, class_name):
        """
        依据类名获取Field
        """
        target_pattern = class_name.split('NodeSerializer')[0].lower()
        fields = self._fields.keys()
        for field in fields:
            if re.match(target_pattern, field):
                return field

    def validate(self, data):
        if data.get('report') is None and data.get('node_type') == 'ROOT':
            raise serializers.ValidationError("report must be specified.")
        else:
            return data

    @transaction.atomic
    def recursive_create(self, validated_data, report=None):
        based_fields = ('section_uuid', 'json_path', 'report', 'created_time',
                        'node_type', 'section_node_set')
        fields = self._fields.keys()
        # 集合差运算
        node_fields = list(set(fields).difference(set(based_fields)))
        # 匹配所有类名中含有NodeSerializer字符串的类
        serializer_class_dict = {self.get_field_name(item): globals().get(item)
                                 for item in globals().keys()
                                 if re.match('.*NodeSerializer', item)}

        validated_data = {key: value for key, value in validated_data.items()
                          if value is not None}

        section_node_set = validated_data.get('section_node_set')
        section_node_lst = []
        field_dict = {}
        if section_node_set:
            pop_field(validated_data, 'section_node_set')

            for section_node in section_node_set:
                section_node_instance = self.recursive_create(section_node)
                section_node_lst.append(section_node_instance)

        for field in node_fields:
            if validated_data.get(field):
                node_field_data = validated_data.pop(field)
                serializer_class = serializer_class_dict.get(field)
                assert serializer_class is not None
                serializer = serializer_class(data=node_field_data)
                print("serializer", node_field_data, serializer_class, serializer.is_valid(), serializer.errors)
                if serializer.is_valid():
                    field_data = serializer.validated_data
                    instance_uuid = uuid.uuid1()
                    prefix = field.split('_node')[0]
                    key = "%s_uuid" % prefix
                    field_data.update({key: instance_uuid})
                    field_instance = serializer.create(field_data)
                    field_dict.update({field: field_instance})

        pop_field(validated_data, 'section_uuid')
        section_uuid = uuid.uuid1()
        print("field_dict", field_dict)
        parent_section_node = SectionNode.objects.create(section_uuid=section_uuid,
                                                         **field_dict,
                                                         **validated_data)
        if len(section_node_lst) > 0:
            for section_node in section_node_lst:
                parent_section_node.section_node.add(section_node)
        return parent_section_node

    @transaction.atomic
    def create(self, validated_data):
        if validated_data.get('version'):
            version = validated_data.pop('version')
        else:
            version = None
        # 递归创建section_node
        section_node = self.recursive_create(validated_data)
        # 更新report版本指针
        report = validated_data.get('report')
        report.latest = section_node.section_uuid
        report.save()

        version_uuid = section_node.section_uuid
        if version is None:
            version = {
                'version_uuid': version_uuid,
                'name_alias': timezone.now()
            }
        version = Version.objects.create(**version)
        report.version_set.add(version)
        return section_node


class ReportNodeSerializer(serializers.ModelSerializer):
    report_uuid = serializers.UUIDField(format='hex_verbose', required=False,
                                        validators=[UniqueValidator(queryset=ReportNode.objects.all())])
    version_set = VersionSerializer(many=True, required=False)
    created_time = serializers.DateTimeField(required=False)
    updated_time = serializers.DateTimeField(required=False)
    owner = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = ReportNode
        fields = ('report_uuid', 'version_set', 'latest', 'created_time',
                  'updated_time', 'patient', 'owner')

    def exist_version_item(self, version_uuid):
        version = Version.objects.filter(version_uuid=version_uuid)
        if version:
            return True
        else:
            return False

    @transaction.atomic
    def update_version_set(self, instance, version_set):
        for version_validated_data in version_set:
            version_uuid = version_validated_data.get('version_uuid')
            if not self.exist_version_item(version_uuid):
                version_uuid = Version.objects.create(**version_validated_data)
            instance.version_set.add(version_uuid)

    @transaction.atomic
    def create(self, validated_data):
        updated_time = created_time = timezone.now()
        report_uuid = uuid.uuid1()
        user = self.context['request'].user
        print(user.__class__)
        if user.__class__ == AnonymousUser:
            user = User.objects.filter(is_staff=True).first()
            # TODO: user is None return 400 status code

        pop_field(validated_data, 'report_uuid')
        report = ReportNode.objects.create(user=user,
                                           report_uuid=report_uuid,
                                           created_time=created_time,
                                           updated_time=updated_time,
                                           **validated_data)
        report.save()
        if validated_data.get('version_set'):
            version_set = validated_data.pop('version_set')
            self.update_version_set(report, version_set)
        return report

    @transaction.atomic
    def update(self, instance, validated_data):
        if validated_data.get('version_set'):
            version_set = validated_data.pop('version_set')
            self.update_version_set(instance, version_set)
        updated_time = timezone.now()
        instance.user = validated_data.get('owner', instance.user)
        instance.patient = validated_data.get('patient', instance.patient)
        instance.updated_time = updated_time
        instance.latest = validated_data.get('latest', instance.latest)
        instance.save()
