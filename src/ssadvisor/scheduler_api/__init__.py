# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import sys
import traceback


def _load(path, module_name, modulelist=['slurm', 'torque']):
    loader = __import__(path, fromlist=modulelist)
    return getattr(loader,
                   '%s.%sScheduler' % (module_name, module_name.capitalize()))


def get_scheduler(scheduler_name='slurm'):
    try:
        scheduler_name = scheduler_name.lower()
        scheduler_cls = _load('ssadvisor.scheduler_api', '%s' % scheduler_name)
        return scheduler_cls
    except AttributeError:
        raise ImportError('scheduler %s cannot be found (%s)' %
                          (scheduler_name,
                           traceback.format_exception(*sys.exc_info())))
