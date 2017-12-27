# -*- coding: utf-8 -*-
import logging, copy
from datetime import datetime
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.core.validators import MaxValueValidator

logger = logging.getLogger(__name__)

class Setting(models.Model):
    PLATFORMS = (
        ('Linux', 'Linux'),
        ('linux', 'Linux'),
        ('osx', 'OSX'),
        ('OSX', 'OSX'),
        ('win', 'WIN'),
        ('WIN', 'WIN')
    )
    ARCHS = (
        ('X86_64', 'X86_64'),
        ('x86_64', 'x86_64'),
        ('x86', 'X86'),
        ('X86', 'X86')
    )
    setting_uuid = models.CharField(max_length = 36, primary_key = True)
    name = models.CharField(max_length = 16)
    summary = models.TextField(null = True)
    # For conda ROOT_PREFIX
    cobweb_root_prefix = models.CharField(max_length = 255, default = '/opt/local/cobweb')
    cobweb_platform = models.CharField(max_length = 8, default = 'Linux', choices = PLATFORMS)
    cobweb_arch = models.CharField(max_length = 8, default = 'X86_64', choices = ARCHS)
    # For saving repodata.json and total_pkgs.json
    cobweb_home = models.CharField(max_length = 255, default = '.')
    is_active = models.BooleanField(null = False, default = False)

    class Meta:
        ordering = ('name',)
        permissions = (("list_setting", "can list setting instance(s)"),)

    def __str__(self):
        return "%s" % (self.name)


class Channel(models.Model):
    ARCHS = (
        ('x86_64', 'X86_64'),
        ('X86_64', 'X86_64'),
        ('x86', 'X86'),
        ('X86', 'X86'),
    )
    PLATFORMS = (
        ('linux', 'LINUX'),
        ('LINUX', 'LINUX'),
        ('osx', 'OSX'),
        ('OSX', 'OSX'),
    )
    channel_uuid = models.CharField(max_length = 36, primary_key = True)
    channel_name = models.CharField(max_length = 32, unique = True, db_index = True)
    arch = models.CharField(max_length = 16, choices = ARCHS)
    platform = models.CharField(max_length = 8, choices = PLATFORMS)
    channel_path = models.CharField(max_length = 255, unique = True, db_index = True)
    md5sum = models.CharField(max_length = 32, unique = True)    # repodata.json文件md5值
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(null = True)
    is_active = models.BooleanField(null = False, default = True)
    summary = models.TextField(null = True)
    priority_level = models.PositiveSmallIntegerField(default = 10,
                                                      validators=[MaxValueValidator(10),])    # Channel优先级，Level值越低级别越高
    is_alive = models.BooleanField(null = False, default = True)    # Channel是否在线
    total_pkgs_num = models.PositiveIntegerField(default = 0)

    def __str__(self):
        return '%s' % (self.channel_uuid)

    class Meta:
        ordering = ('is_active', 'is_alive', 'channel_name', 'updated_time')
        permissions = (("list_channel", "can list channel instance(s)"),)

class Package(models.Model):
    """
    Package的管理是以Conda Environment的安装为对象，不考虑依赖安装，只考虑以create -n方式
    独立安装的Package(类似于360软件管家)
    """
    pkg_uuid = models.CharField(max_length = 36, primary_key = True)
    md5sum = models.CharField(max_length = 32, unique = True)
    build = models.CharField(max_length = 128, null = True)
    build_number = models.PositiveIntegerField(null = True)
    created_date = models.DateField(null = True)
    license = models.CharField(max_length = 255, null = True)
    license_family = models.CharField(max_length = 255, null = True)
    name = models.CharField(max_length = 128)
    size = models.PositiveIntegerField()
    depends = models.TextField(null = True)
    version = models.CharField(max_length = 64, null = True)
    pkg_name = models.CharField(max_length = 255, unique = True)
    summary = models.TextField(null = True)
    url = models.CharField(max_length = 255, null = True)
    refereces = models.TextField(null = True)
    is_workflow = models.BooleanField(null = False, default = False)
    is_cluster_pkg = models.BooleanField(null = False, default = False)
    created_author = models.CharField(max_length = 64, null = True)
    # 前端参数变量模板(描述输入)
    frontend_templ = models.CharField(max_length = 255, null = True)
    # 输出文件变量模板(描述输出)
    output_templ = models.CharField(max_length = 255, null = True)
    # 报告文件模板(描述报告)
    report_templ = models.CharField(max_length = 255, null = True)
    # Spider模板(描述Spider配置文件)
    spider_templ = models.CharField(max_length = 255, null = True)
    # Module File模板(描述Module Environment配置文件)
    module_templ = models.CharField(max_length = 255, null = True)
    is_installed = models.BooleanField(null = False, default = False)
    env_name = models.CharField(max_length = 255, null = True)
    installed_time = models.DateTimeField(null = True)
    first_channel = models.CharField(max_length = 128)
    channels = models.ManyToManyField(Channel)

    class Meta:
        ordering = ('pkg_name', 'is_installed')
        permissions = (("list_package", "can list package instance(s)"),)

    def __str__(self):
        return "%s" % (self.pkg_uuid)

    # def clean(self):
    #     if self.is_cluster_pkg and not self.module_templ:
    #         raise ValidationError(_('Need a module template file when the type \
    #                                  of a package is cluster.'))
    #
    #     if self.is_workflow and not (self.frontend_templ and self.output_templ \
    #                                  and self.report_templ and self.spider_templ):
    #         raise ValidationError(_('Need a frontend_templ, output_templ, \
    #                                  report_templ, and spider_templ when the type\
    #                                  of a package is workflow'))


class Log(models.Model):
    pass
