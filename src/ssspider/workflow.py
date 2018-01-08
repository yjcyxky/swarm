# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

from collections import OrderedDict
from persistent import Persistent

class SpiderInfo(Persistent):
    def __init__(self):
        self._d3dag = None
        self._progress = dict()
        self._log = OrderedDict()
        self._rule_info = list()
        self._job_info = list()
        self._run_info = list()
        self._resources_info = list()
        self._shellcmds = list()
        self._dag_debug = list()

    def handler(self, msg):
        level = msg.get('level')
        msg = msg.get('msg')

        if level == 'info':
            self._log['info'] = msg
        elif level == 'warning':
            self._log['warning'] = msg
        elif level == 'debug':
            self._log['debug'] = msg
        elif level == 'error':
            self._log['error'] = msg
        elif level == 'progress':
            self._progress = msg
        elif level == 'resources_info':
            self._resources_info.append(msg)
        elif level == 'run_info':
            self._run_info.append(msg)
        elif level == 'job_info':
            self._job_info.append(msg)
        elif level == 'job_error':
            self._job_info.append(msg)
        elif level == 'job_finished':
            self._job_info.append(msg)
        elif level == 'dag_debug':
            self._dag_debug.append(msg)
        elif level == 'shellcmd':
            self._shellcmds.append(msg)
        elif level == 'rule_info':
            self._rule_info.append(msg)
        elif level == 'd3dag':
            self._d3dag = msg

def get_log_handler(path, filename, debug = False):
    from ssspider.ZODB import SpiderZODB, transaction
    import json
    import os
    if not os.path.isdir(path):
        os.makedirs(path)

    zodb_path = os.path.join(path, filename)
    debug_file_path = os.path.join(path, 'debug.txt')

    def output_debug(file_path, msg):
        with open(file_path, 'a+') as f:
            f.write(str(msg))
            f.write('\n\n--------\n\n')

    def log_handler(msg):
        db = SpiderZODB(zodb_path)
        dbroot = db.dbroot
        spider_info = dbroot.get('spider_info')

        if spider_info is None:
            spider_info = SpiderInfo()
        spider_info.handler(msg)

        dbroot['spider_info'] = spider_info
        transaction.commit()
        db.close()

        if debug:
            output_debug(debug_file_path, msg)

    return log_handler
