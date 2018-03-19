import os
import sys
import unittest
from os.path import dirname as get_dirname
from django.test import TestCase
from django.conf import settings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = get_dirname(get_dirname(get_dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)

from report_engine.models import get_report_engine_home
from report_engine.models import (TitleNode, InfoNode, ParagraphNode, UrlNode,
                                  MediaNode, ReferenceNode, HeaderNode,
                                  FooterNode, ListNode, TableNode, Version,
                                  ReportNode, SectionNode)
from bin.cli import setup_django


class TestFunc(TestCase):
    """
    测试report_engine模块中定义的函数
    """
    def setUp(self):
        """
        设置Django运行环境
        """
        setup_django()

    def tearDown(self):
        """
        清扫战场
        """
        pass

    def test_get_report_engine_home_no_create(self):
        report_engine_home = get_report_engine_home(create_flag=False)
        settings_report_engine_home = getattr(settings, 'REPORT_ENGINE_HOME')
        assert report_engine_home == settings_report_engine_home

        if not settings_report_engine_home:
            USER_HOME = os.path.expanduser("~")
            DEFAULT_HOME = os.path.join(USER_HOME, 'report_engine')
            assert report_engine_home == DEFAULT_HOME

    def test_get_report_engine_home_create(self):
        report_engine_home = get_report_engine_home(create_flag=True)
        assert os.path.isdir(report_engine_home) is True
        os.rmdir(report_engine_home)

if __name__ == '__main__':
    unittest.main()
