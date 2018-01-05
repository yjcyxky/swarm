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
import requests
import hashlib
import os
import json
import uuid
import time
from errno import ENOENT
from urllib.error import HTTPError
from rest_framework import status
from django.db.models import Q
from django.db import transaction
from sscobweb.exceptions import (CobwebNoChannel, CobwebExistChannel,
                                 CobwebPkgExistsError, CobwebNoSuchPackages,
                                 CobwebWrongSetting)
from sscobweb.models import Channel as ChannelModel
from sscobweb.models import Package
from sscobweb.models import CobwebSetting

logger = logging.getLogger(__name__)

def get_settings():
    try:
        settings = CobwebSetting.objects.filter(is_active = 1).order_by('is_active')
        current_setting = settings[0]
        return current_setting
    except CobwebSetting.DoesNotExist:
        raise CobwebWrongSetting('Cobweb Wrong Setting.')

class Channel:
    def __init__(self, channel_name, channel_path, dest_dir = None):
        self.settings = get_settings()
        self._channel_name = channel_name
        if dest_dir:
            self._dest_dir = dest_dir
        else:
            self._dest_dir = self.settings.cobweb_home
        self._new_pkgs = None
        self._existed_pkgs = None
        self._created_time = None
        self._repodata = None
        self._channel_uuid = None
        self._total_pkgs_path = os.path.join(self._dest_dir, 'total_pkgs.json')

        channel_path = channel_path.strip()
        if 'repodata.json' not in channel_path.split('/'):
            self._channel_path = os.path.join(channel_path, 'repodata.json')
        else:
            self._channel_path = channel_path

        if self.exist_channel(md5sum = False):
            # 更新repo而非增加新的repo
            self._update_repo = True
            try:
                self._channel = ChannelModel.objects.get(channel_name = self._channel_name)
            except:
                raise CobwebNoChannel("Not Found Channel %s" % self._channel_name)
        else:
            self._update_repo = False
            self._channel = None

        if not os.path.isdir(self._dest_dir):
            raise IOError(ENOENT, 'No such directory', self._dest_dir)

        if not os.path.isfile(self._total_pkgs_path) or not ChannelModel.objects.all():
            # 初始化
            self._total_pkgs = []
        else:
            with open(os.path.join(self._dest_dir, 'total_pkgs.json'), 'r') as f:
                self._total_pkgs = json.load(f)
        # logger.debug("sscobweb@utils@Channel@__init__@_total_pkgs@%s" % self._total_pkgs)

    def get_total_pkgs(self, dest_dir):
        return self._total_pkgs

    def fetch_repodata(self):
        scheme = self._check_scheme()
        if scheme in ("http", "https", "ftp", "file"):
            try:
                r = requests.get(self._channel_path, timeout = 5)
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
                raise CobwebNoChannel("Not Found Channel %s" % self._channel_path)
            repodata = r.content
            if r.status_code == requests.codes.ok:
                created_time = time.localtime(time.time())
                self._created_time = time.strftime("%Y-%m-%d %H:%M:%S", created_time)
                logger.debug("sscobweb@utils@fetch_repodata@created_time@%s" % self._created_time)

                # logger.debug("sscobweb@utils@Channel@fetch_repodata@repodata@%s" % repodata)
                self._md5sum = hashlib.md5(repodata).hexdigest()
                logger.debug("sscobweb@utils@Channel@fetch_repodata@md5sum@%s" % self._md5sum)
                self._repodata = json.loads(repodata.decode('utf8').replace("'", '"'))
            else:
                raise CobwebNoChannel("Not Found Channel %s" % self._channel_path)

        if self.exist_channel():
            raise CobwebExistChannel("Exist Channel %s" % self._channel_path)

        self._copy2repo()
        pkgs = self._diff_repodata(self._repodata.get('packages').keys())
        self._new_pkgs = pkgs.get('new_pkgs')
        self._existed_pkgs = pkgs.get('existed_pkgs')

        # logger.debug("sscobweb@utils@Channel@fetch_repodata@existed_pkgs@%s" % str(self._existed_pkgs))
        # logger.debug("sscobweb@utils@Channel@fetch_repodata@new_pkgs@%s" % str(self._new_pkgs))
        # logger.debug("sscobweb@utils@Channel@fetch_repodata@repodata@%s" % str(self._repodata))

    @transaction.atomic
    def sync(self):
        if not self._new_pkgs:
            self.fetch_repodata()

        self._gen_total_pkgs()
        if self._update_repo:
            self._update_channel()
            self._add_new_pkgs()
            self._update_existed_pkgs()
        else:
            self._add_new_channel()
            self._add_new_pkgs()
            self._update_existed_pkgs()

    def exist_channel(self, md5sum = True):
        """
        数据库中是否已经存在相关记录
        """
        try:
            if md5sum:
                if ChannelModel.objects.get(md5sum = self._md5sum):
                    return True
            else:
                if ChannelModel.objects.get(channel_path = self._channel_path):
                    return True
        except ChannelModel.DoesNotExist:
            return False

    def _gen_total_pkgs(self):
        with open(self._total_pkgs_path, 'w') as f:
            self._total_pkgs.extend(self._new_pkgs)
            self._total_pkgs.sort()
            f.write(json.dumps(self._total_pkgs))

    def _diff_repodata(self, pkgs):
        new_pkgs = set(pkgs) - set(self._total_pkgs)
        existed_pkgs = set(pkgs) - set(new_pkgs)
        return {
            'new_pkgs': tuple(new_pkgs),
            'existed_pkgs': tuple(existed_pkgs)
        }

    def _update_channel(self):
        try:
            if self._channel:
                self._channel.update(updated_time = self._created_time)
                self._channel.save
        except:
            pass

    def _update_channels(self, channel_uuid):
        relations = []
        ChannelPackageRelation = Package.channels.through
        pkgs = Package.objects.filter(first_channel = channel_uuid)
        for pkg in pkgs:
            relations.append(ChannelPackageRelation(channel_id = channel_uuid,
                                                    package_id = pkg.pkg_uuid))
        ChannelPackageRelation.objects.bulk_create(relations)

    def _update_existed_pkgs(self):
        ChannelPackageRelation = Package.channels.through
        relations = []
        channel_uuid = self._channel.channel_uuid
        if self._update_repo:
            pkgs = Package.objects.filter(Q(channels__channel_uuid__exact = \
                                             self._channel.channel_uuid))
            for pkg in pkgs:
                relations.append(ChannelPackageRelation(channel_id = channel_uuid,
                                                        package_id = pkg.id))
        else:
            pkgs = Package.objects.all()
            for pkg in pkgs:
                if pkg.pkg_name in self._existed_pkgs:
                    relations.append(ChannelPackageRelation(channel_id = channel_uuid,
                                                            package_id = pkg.id))
        ChannelPackageRelation.objects.bulk_create(relations)

    def _add_new_channel(self):
        info = self._repodata.get('info')
        total_pkgs_num = len(self._repodata.get('packages'))
        channel_data = {
            'channel_uuid': str(uuid.uuid4()),
            'channel_name': self._channel_name,
            'arch': info.get('arch'),
            'platform': info.get('platform'),
            'channel_path': self._channel_path,
            'md5sum': self._md5sum,
            'created_time': self._created_time,
            'updated_time': self._created_time,
            'is_active': True,
            'summary': info.get('summary'),
            'priority_level': 10,
            'is_alive': True,
            'total_pkgs_num': total_pkgs_num
        }
        self._channel = ChannelModel.objects.create(**channel_data)
        self._channel.save()

    def _add_new_pkgs(self):
        pkgs_list = list()
        for pkg in self._new_pkgs:
            pkg_info = self._repodata.get('packages').get(pkg)
            validated_data = {
                'pkg_uuid': uuid.uuid4(),
                'name': pkg_info.get('name'),
                'pkg_name': pkg,
                'md5sum': pkg_info.get('md5'),
                'build': pkg_info.get('build'),
                'build_number': pkg_info.get('build_number'),
                'created_date': pkg_info.get('date'),
                'installed_time': None,
                'license': pkg_info.get('license'),
                'license_family': pkg_info.get('license_family'),
                'size': pkg_info.get('size'),
                'depends': str(pkg_info.get('depends')),
                'version': pkg_info.get('version'),
                'summary': pkg_info.get('summary'),
                'url': pkg_info.get('url'),
                'refereces': pkg_info.get('refereces'),
                'is_workflow': pkg_info.get('is_workflow', False),
                'is_cluster_pkg': pkg_info.get('is_cluster_pkg', False),
                'created_author': pkg_info.get('created_author'),
                'first_channel': self._channel.channel_uuid,
                'frontend_templ': None,
                'output_templ': None,
                'report_templ': None,
                'spider_templ': None,
                'module_templ': None,
                'is_installed': False
            }
            # logger.debug("sscobweb@utils@_add_new_pkgs@validated_data@%s" % str(validated_data))
            # pkg = Package(**validated_data)
            # pkg.save()
            # pkg.channels.add(self._channel)
            pkgs_list.append(Package(**validated_data))
        # logger.debug("sscobweb@utils@_add_new_pkgs@pkgs_list@%s" % str(pkgs_list))
        division = len(pkgs_list) // 1000
        for idx in range(division):
            Package.objects.bulk_create(pkgs_list[idx * 1000:(idx + 1) * 1000])
        Package.objects.bulk_create(pkgs_list[division * 1000:len(pkgs_list)])
        self._update_channels(self._channel.channel_uuid)

    def _copy2repo(self):
        path = os.path.join(self._dest_dir, self._channel_name)
        repo_file_path = os.path.join(path, 'repodata.json')
        if not os.path.isdir(path):
            os.makedirs(path)
        if os.path.isfile(repo_file_path):
            created_time = time.localtime(os.path.getctime(repo_file_path))
            created_time = time.strftime("%Y_%m_%d_%H_%M_%S", created_time)
            os.rename(repo_file_path, os.path.join(path, 'repodata_%s.json' % created_time))

        with open(repo_file_path, 'w') as fw:
            fw.write(json.dumps(self._repodata))

    def _get_created_time(self):
        scheme = self._check_scheme()
        if scheme in ("http", "https", "ftp", "file"):
            with requests.get(self._channel_path, stream = True) as conn:
                created_time = conn.headers['last-modified']
                return created_time

    def _check_channel_alive(self):
        channel_path = self._channel_path
        scheme = self._check_scheme()
        if scheme in ("http", "https", "ftp", "file"):
            with requests.get(channel_path, stream = True) as conn:
                if conn.status_code == requests.codes.ok:
                    return True
        if os.path.isfile(channel_path):
            return True
        return False

    def _check_scheme(self):
        scheme_dict = {
            "http": r"^https?:/{2}\w.+$",
            "ftp": r"^ftp:/{2}\w.+$",
            "file": r"^file:/{3}\w.+$"
        }
        for (key, pattern) in scheme_dict.items():
            if re.match(pattern, self._channel_path):
                return key
        return 'local'


class Conda:
    def __init__(self, pkg_uuid, prefix = None,
                 conda_api_path = 'sscobweb.conda_api'):
        # TODO: 如何解决同一版本Package多个build的问题？
        self._pkg_uuid = pkg_uuid
        self.settings = get_settings()

        try:
            self._pkg = Package.objects.get(pkg_uuid = self._pkg_uuid)
            self._env_name = '%s-%s' % (self._pkg.name, self._pkg.version)
        except Package.DoesNotExist:
            logger.error("No such Package %s." % self._pkg_uuid)
            raise Package.DoesNotExist

        try:
            self.conda_api = self._load_loader(conda_api_path)
        except ImportError:
            logger.debug("No such Module: %s." % conda_api_path)

        if self.conda_api.ROOT_PREFIX is None:
            self._prefix = self.settings.cobweb_root_prefix
            self.conda_api.set_root_prefix(prefix = self._prefix)

    def _load_loader(self, name):
        loader = __import__(name, fromlist=['conda_api'])
        return loader.conda_api

    def _get_channels(self):
        # TODO: 增加过滤，.condarc文件只添加package相关的库与base库
        # 所有自定义软件依赖的包均放置在base库中
        arch = self.settings.cobweb_arch
        platform = self.settings.cobweb_platform
        filters = (Q(is_active__exact = 1),
                   Q(is_alive__exact = 1),
                   Q(arch__exact = arch),
                   Q(platform__exact = platform))
        channels = ChannelModel.objects.filter(*filters) \
                                       .order_by('priority_level')
        if channels:
            valid_channels = self._pkg.channels
            logger.debug('Cobweb@utils@_get_channels@valid_channels@%s' % str(valid_channels))
            return [channel.channel_path for channel in channels]
        else:
            return []

    def _update_status(self, is_installed):
        """
        更新安装状态
        """
        logger.debug('Cobweb@utils@_update_status@is_installed@%s to %s' % (self._pkg.is_installed, is_installed))
        self._pkg.is_installed = bool(is_installed)
        if is_installed:
            self._pkg.env_name = self._env_name
            self._pkg.installed_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        else:
            self._pkg.env_name = None
            self._pkg.installed_time = None
        self._pkg.save()

    def get_env_name(self):
        return self._env_name

    def reset_channels(self):
        try:
            if self.conda_api.config_get('channels'):
                warnings = self.conda_api.config_delete('channels')
                logger.debug("Conda@reset_channels@warnings@%s" % str(warnings))

            channels = self._get_channels()
            for channel in channels:
                self.conda_api.config_add('channels', channel)
                logger.debug("Conda@reset_channels@channel@%s" % str(channel))
        except self.conda_api.CondaError as e:
            logger.debug("Conda@reset_channels@%s" % str(e))

    def install(self):
        """
        所有的Package均以create -n env_name的形式安装，以尽可能的保证互不干扰，类似于Windows安装包
        """
        # 软件安装规范：cobweb_home/envs/`pkg_name`-`pkg_version`/
        try:
            pkg = '%s=%s' % (self._pkg.name, self._pkg.version)
            out = self.conda_api.create(name = self._env_name, pkgs = (pkg,))
            self._update_status(is_installed = True)
            return self._pkg
        except (TypeError, self.conda_api.CondaEnvExistsError) as err:
            raise CobwebPkgExistsError('%s already exists' % self._env_name,
                                       status_code = status.HTTP_400_BAD_REQUEST)

    def remove(self):
        try:
            out = self.conda_api.remove_environment(name = self._env_name)
            self._update_status(is_installed = False)
            logger.debug("Conda@remove@env_name@%s" % self._env_name)
            return self._pkg
        except self.conda_api.CondaError as e:
            raise CobwebNoSuchPackages("No Such Installed Packages.")
