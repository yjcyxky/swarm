# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

from __future__ import absolute_import
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import setproctitle
from bin import configuration as conf

def post_worker_init(dummy_worker):
    setproctitle.setproctitle(
        conf.GUNICORN_WORKER_READY_PREFIX + setproctitle.getproctitle()
    )
