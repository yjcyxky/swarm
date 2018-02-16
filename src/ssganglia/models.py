# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import os
import logging
import rrdtool
import uuid
import time
from django.db import models, DatabaseError
from ssganglia.exceptions import RrdCfException

logger = logging.getLogger(__name__)


class RRDConfigModel(models.Model):
    uuid = models.CharField(max_length=36, primary_key=True)
    filename = models.CharField(max_length=255, unique=True)
    hostname = models.CharField(max_length=255)
    # host = models.ForeignKey(Host, on_delete=models.CASCADE)
    clustername = models.CharField(max_length=255)
    metric = models.CharField(max_length=255)
    metric_type = models.CharField(max_length=8)
    metric_alias = models.CharField(max_length=32, null=True)

    def __str__(self):
        return '%s-%s-%s' % (self.uuid, self.hostname, self.metric)

    class Meta:
        ordering = ('clustername', 'hostname', 'metric')
        permissions = (("list_config", "can list config instance(s)"),)


class RRDConfig:
    """
    扫描Ganglia rrd目录，解析获取Ganglia主机/集群配置，并写入数据库
    """
    def __init__(self, rrd_path):
        self.rrd_abs_path = os.path.abspath(rrd_path)

    def get_all_rrd_files(self):
        logger.info("获取%s目录下所有RRD文件..." % self.rrd_abs_path)
        self.all_files = [os.path.join(dp, f) for dp, dn, fs in
                          os.walk(self.rrd_abs_path) for f in fs
                          if os.path.splitext(f)[1] == '.rrd']
        return self.all_files

    def get_metrics_meta(self):
        logger.info("获取所有Metrics Metadata信息")
        all_files = self.get_all_rrd_files()
        self.metrics_meta_dict = []
        for rrd_file in all_files:
            result = rrdtool.info(rrd_file)
            filepath = result.get('filename')
            metric_type = [value for key, value in result.items()
                           if '.type' in key.lower()]
            self.metrics_meta_dict.append({
                "uuid": uuid.uuid4(),
                "filename": filepath,
                "hostname": rrd_file.split('/')[-2],
                "clustername": rrd_file.split('/')[-3],
                "metric": os.path.basename(filepath).split('.')[0],
                "metric_type": metric_type[0] if len(metric_type) != 0 else None
            })
        return self.metrics_meta_dict

    def write2db(self):
        for metric_meta in self.metrics_meta_dict:
            try:
                logger.info("新增metric metadata：%s" % str(metric_meta))
                rrd_config_model = RRDConfigModel(**metric_meta)
                rrd_config_model.save()
            except DatabaseError as err:
                logger.error("存入数据库错误-%s-%s" % (str(metric_meta), str(err)))
                continue

    def sync2db(self):
        self.get_metrics_meta()
        self.write2db()


class RRDData:
    """
    解析rrd文件，获取记录
    """
    def __init__(self, rrd_file_path):
        self.rrd_file_path = os.path.abspath(rrd_file_path)

    def fetch_data(self, start=0, end=time.time(), resolution=1, cf='AVERAGE'):
        """
        封装rrdtool.fetch，查询rrd文件中的记录
        返回元祖，metadata与rrd记录
        """
        if cf not in ('AVERAGE', 'MIN', 'MAX', 'LAST'):
            raise RrdCfException("CF must be one of \
                                  'AVERAGE', 'MIN', 'MAX' and 'LAST'")
        import rrdtool
        args = ['-r', str(resolution), '--start', str(start),
                '--end', str(end)]
        rrd_src_data = rrdtool.fetch(self.rrd_file_path, "AVERAGE", *args)
        start, end, step = rrd_src_data[0]

        rrd_json_data = []
        timestamp = start
        for value in rrd_src_data[2]:
            rrd_json_data.append({
                "timestamp": timestamp,
                "value": value[0]
            })
            timestamp = timestamp + step

        # 从数据库中获取metadata
        rrd_meta = RRDConfigModel.objects.get(filename=self.rrd_file_path)

        return (rrd_meta, rrd_json_data)
