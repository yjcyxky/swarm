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
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from lib.rest_framework_recursive.fields import RecursiveField
from report_engine.models import (SectionNode, get_report_engine_home, Version,
                                  ReportNode, TitleNode, InfoNode, ParagraphNode,
                                  MediaNode, UrlNode, ReferenceNode, HeaderNode,
                                  FooterNode, ListNode, TableNode)

logger = logging.getLogger(__name__)

def check_path(path):
    RE = re.compile("^/[a-zA-Z0-9\-_/]+$")
    match = re.match(RE, path)
    if match is None:
        raise serializers.ValidationError('Not a valid path, you must specify the path as an unix absolute path')


class TitleNodeSerializer(serializers.ModelSerializer):
    title_uuid = serializers.UUIDField(format = 'hex_verbose', read_only = True)
    content = serializers.JSONField(binary = True)

    class Meta:
        model = TitleNode
        fields = ('title_uuid', 'created_time', 'content')


class InfoNodeSerializer(serializers.ModelSerializer):
    info_uuid = serializers.UUIDField(format = 'hex_verbose', read_only = True)
    content = serializers.JSONField(binary = True)

    class Meta:
        model = InfoNode
        fields = ('info_uuid', 'created_time', 'content')


class ParagraphNodeSerializer(serializers.ModelSerializer):
    paragraph_uuid = serializers.UUIDField(format = 'hex_verbose', read_only = True)
    content = serializers.JSONField(binary = True)

    class Meta:
        model = ParagraphNode
        fields = ('paragraph_uuid', 'created_time', 'content')


class MediaNodeSerializer(serializers.ModelSerializer):
    media_uuid = serializers.UUIDField(format = 'hex_verbose', read_only = True)
    content = serializers.JSONField(binary = True)

    class Meta:
        model = MediaNode
        fields = ('media_uuid', 'created_time', 'content')


class UrlNodeSerializer(serializers.ModelSerializer):
    url_uuid = serializers.UUIDField(format = 'hex_verbose', read_only = True)
    content = serializers.JSONField(binary = True)

    class Meta:
        model = UrlNode
        fields = ('url_uuid', 'created_time', 'content')


class ReferenceNodeSerializer(serializers.ModelSerializer):
    reference_uuid = serializers.UUIDField(format = 'hex_verbose', read_only = True)
    content = serializers.JSONField(binary = True)

    class Meta:
        model = ReferenceNode
        fields = ('reference_uuid', 'created_time', 'content')


class HeaderNodeSerializer(serializers.ModelSerializer):
    header_uuid = serializers.UUIDField(format = 'hex_verbose', read_only = True)
    content = serializers.JSONField(binary = True)

    class Meta:
        model = HeaderNode
        fields = ('header_uuid', 'created_time', 'content')


class FooterNodeSerializer(serializers.ModelSerializer):
    footer_uuid = serializers.UUIDField(format = 'hex_verbose', read_only = True)
    content = serializers.JSONField(binary = True)

    class Meta:
        model = FooterNode
        fields = ('footer_uuid', 'created_time', 'content')


class ListNodeSerializer(serializers.ModelSerializer):
    list_uuid = serializers.UUIDField(format = 'hex_verbose', read_only = True)
    content = serializers.JSONField(binary = True)

    class Meta:
        model = ListNode
        fields = ('list_uuid', 'created_time', 'content')


class TableNodeSerializer(serializers.ModelSerializer):
    table_uuid = serializers.UUIDField(format = 'hex_verbose', read_only = True)
    content = serializers.JSONField(binary = True)

    class Meta:
        model = TableNode
        fields = ('table_uuid', 'created_time', 'content')


class VersionSerializer(serializers.ModelSerializer):
    version_uuid = serializers.UUIDField(format = 'hex_verbose', read_only = True)

    class Meta:
        model = Version
        fields = ('version_uuid', 'created_time', 'name_alias')


class SectionNodeSerializer(serializers.ModelSerializer):
    section_uuid = serializers.UUIDField(format = 'hex_verbose', read_only = True)
    created_time = serializers.DateTimeField()
    json_path = serializers.CharField(validators = [check_path, ], allow_null = True)
    title_node = TitleNodeSerializer(allow_null = True)
    info_node = InfoNodeSerializer(allow_null = True)
    paragraph_node = ParagraphNodeSerializer(allow_null = True)
    media_node = MediaNodeSerializer(allow_null = True)
    url_node = UrlNodeSerializer(allow_null = True)
    reference_node = ReferenceNodeSerializer(allow_null = True)
    header_node = HeaderNodeSerializer(allow_null = True)
    footer_node = FooterNodeSerializer(allow_null = True)
    list_node = ListNodeSerializer(allow_null = True)
    table_node = TableNodeSerializer(allow_null = True)
    section_node = RecursiveField(allow_null = True)
    report = serializers.PrimaryKeyRelatedField(queryset = ReportNode.objects.all(),
                                                pk_field = serializers.UUIDField(format='hex_verbose'))

    class Meta:
        model = SectionNode
        fields = ('section_uuid', 'section_node', 'created_time', 'node_type',
                  'title_node', 'info_node', 'paragraph_node', 'media_node',
                  'url_node', 'reference_node', 'header_node', 'footer_node',
                  'list_node', 'table_node', 'json_path', 'report')

    def create(self, validated_data):
        print("validated_data", validated_data)


class ReportNodeSerializer(serializers.ModelSerializer):
    report_uuid = serializers.UUIDField(format = 'hex_verbose', read_only = True)
    version_set = VersionSerializer(many = True)
    owner = serializers.ReadOnlyField(source='user.id')
    # root_nodes = SectionNodeSerializer(many = True, read_only = True,
    #                                    source = 'root_node_set')
    root_nodes = serializers.PrimaryKeyRelatedField(many = True,
                                                    queryset = SectionNode.objects.all(),
                                                    pk_field = serializers.UUIDField(format='hex_verbose'),
                                                    source = 'root_node_set')

    class Meta:
        model = ReportNode
        fields = ('report_uuid', 'version_set', 'latest', 'created_time',
                  'updated_time', 'patient', 'owner', 'root_nodes')

    def create(self, validated_data):
        user = self.context['request'].user
        report = ReportNode.objects.create(user = user, **validated_data)
        report.save()
        return report
