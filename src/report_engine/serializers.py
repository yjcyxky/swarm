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
from django.utils import timezone
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from django.db import transaction
from lib.rest_framework_recursive.fields import RecursiveField
from report_engine.models import (SectionNode, Version, ReportNode, TitleNode,
                                  InfoNode, ParagraphNode, MediaNode, UrlNode,
                                  ReferenceNode, HeaderNode, FooterNode,
                                  ListNode, TableNode)

logger = logging.getLogger(__name__)


def check_path(path):
    RE = re.compile("^/[a-zA-Z0-9\-_/\.]+$")
    match = re.match(RE, path)
    if match is None:
        raise serializers.ValidationError("Not a valid path, you must specify"
                                          "the path as an unix absolute path")


class TitleNodeSerializer(serializers.ModelSerializer):
    title_uuid = serializers.UUIDField(format='hex_verbose', read_only=True)
    content = serializers.JSONField(binary=True)

    class Meta:
        model = TitleNode
        fields = ('title_uuid', 'created_time', 'content')


class InfoNodeSerializer(serializers.ModelSerializer):
    info_uuid = serializers.UUIDField(format='hex_verbose', read_only=True)
    content = serializers.JSONField(binary=True)

    class Meta:
        model = InfoNode
        fields = ('info_uuid', 'created_time', 'content')


class ParagraphNodeSerializer(serializers.ModelSerializer):
    paragraph_uuid = serializers.UUIDField(format='hex_verbose',
                                           read_only=True)
    content = serializers.JSONField(binary=True)

    class Meta:
        model = ParagraphNode
        fields = ('paragraph_uuid', 'created_time', 'content')


class MediaNodeSerializer(serializers.ModelSerializer):
    media_uuid = serializers.UUIDField(format='hex_verbose', read_only=True)
    content = serializers.JSONField(binary=True)

    class Meta:
        model = MediaNode
        fields = ('media_uuid', 'created_time', 'content')


class UrlNodeSerializer(serializers.ModelSerializer):
    url_uuid = serializers.UUIDField(format='hex_verbose', read_only=True)
    content = serializers.JSONField(binary=True)

    class Meta:
        model = UrlNode
        fields = ('url_uuid', 'created_time', 'content')


class ReferenceNodeSerializer(serializers.ModelSerializer):
    reference_uuid = serializers.UUIDField(format='hex_verbose',
                                           read_only=True)
    content = serializers.JSONField(binary=True)

    class Meta:
        model = ReferenceNode
        fields = ('reference_uuid', 'created_time', 'content')


class HeaderNodeSerializer(serializers.ModelSerializer):
    header_uuid = serializers.UUIDField(format='hex_verbose', read_only=True)
    content = serializers.JSONField(binary=True)

    class Meta:
        model = HeaderNode
        fields = ('header_uuid', 'created_time', 'content')


class FooterNodeSerializer(serializers.ModelSerializer):
    footer_uuid = serializers.UUIDField(format='hex_verbose', read_only=True)
    content = serializers.JSONField(binary=True)

    class Meta:
        model = FooterNode
        fields = ('footer_uuid', 'created_time', 'content')


class ListNodeSerializer(serializers.ModelSerializer):
    list_uuid = serializers.UUIDField(format='hex_verbose', read_only=True)
    content = serializers.JSONField(binary=True)

    class Meta:
        model = ListNode
        fields = ('list_uuid', 'created_time', 'content')


class TableNodeSerializer(serializers.ModelSerializer):
    table_uuid = serializers.UUIDField(format='hex_verbose', read_only=True)
    content = serializers.JSONField(binary=True)

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
    section_uuid = serializers.UUIDField(format='hex_verbose',
                                         validators=[UniqueValidator(queryset=SectionNode.objects.all())])
    created_time = serializers.DateTimeField()
    json_path = serializers.CharField(validators=[check_path, ],
                                      allow_null=True)
    title_node = TitleNodeSerializer(allow_null=True)
    info_node = InfoNodeSerializer(allow_null=True)
    paragraph_node = ParagraphNodeSerializer(allow_null=True)
    media_node = MediaNodeSerializer(allow_null=True)
    url_node = UrlNodeSerializer(allow_null=True)
    reference_node = ReferenceNodeSerializer(allow_null=True)
    header_node = HeaderNodeSerializer(allow_null=True)
    footer_node = FooterNodeSerializer(allow_null=True)
    list_node = ListNodeSerializer(allow_null=True)
    table_node = TableNodeSerializer(allow_null=True)
    section_node = RecursiveField(allow_null=True)
    report = serializers.PrimaryKeyRelatedField(queryset=ReportNode.objects.all(),
                                                pk_field=serializers.UUIDField(format='hex_verbose'))
    version = VersionSerializer(required=False)

    class Meta:
        model = SectionNode
        fields = ('section_uuid', 'section_node', 'created_time', 'node_type',
                  'title_node', 'info_node', 'paragraph_node', 'media_node',
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

    @transaction.atomic
    def recursive_create(self, validated_data):
        based_fields = ('section_uuid', 'json_path', 'report', 'created_time',
                        'node_type', 'section_node')
        fields = self._fields.keys()
        # 集合差运算
        node_fields = list(set(fields).difference(set(based_fields)))
        # 匹配所有类名中含有NodeSerializer字符串的类
        serializer_class_dict = {self.get_field_name(item): globals().get(item)
                                 for item in globals().keys()
                                 if re.match('.*NodeSerializer', item)}

        validated_data = {key: value for key, value in validated_data.items()
                          if value is not None}

        field_data = validated_data.get('section_node')
        field_dict = {}
        if field_data:
            validated_data.pop('section_node')
            section_node = self.recursive_create(field_data)
            field_dict.update({'section_node': section_node})
        else:
            for field in node_fields:
                if validated_data.get(field):
                    node_field_data = validated_data.pop(field)
                    serializer_class = serializer_class_dict.get(field)
                    assert serializer_class is not None
                    serializer = serializer_class(node_field_data)
                    if serializer.is_valid():
                        field_data = serializer.validated_data
                        field_instance = serializer.create(field_data)
                        field_dict.update({field: field_instance})
        section_node = SectionNode.objects.create(**field_dict,
                                                  **validated_data)
        return section_node

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
    report_uuid = serializers.UUIDField(format='hex_verbose',
                                        validators=[UniqueValidator(queryset=ReportNode.objects.all())])
    version_set = VersionSerializer(many=True)
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
        print(globals())
        user = self.context['request'].user
        version_set = validated_data.pop('version_set')
        report = ReportNode.objects.create(user=user, **validated_data)
        report.save()
        self.update_version_set(report, version_set)
        return report

    @transaction.atomic
    def update(self, instance, validated_data):
        version_set = validated_data.pop('version_set')
        self.update_version_set(instance, version_set)
        instance.user = validated_data.get('owner', instance.user)
        instance.patient = validated_data.get('patient', instance.patient)
        instance.updated_time = validated_data.get('updated_time',
                                                   instance.updated_time)
        instance.latest = validated_data.get('latest', instance.latest)
        instance.save()
