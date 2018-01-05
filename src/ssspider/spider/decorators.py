# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import functools
import inspect

def dec_all_methods(decorator, prefix='test_'):

    def dec_class(cls):
        for name, m in inspect.getmembers(cls, inspect.isfunction):
            if prefix == None or name.startswith(prefix):
                setattr(cls, name, decorator(m))
        return cls

    return dec_class
