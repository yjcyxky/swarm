# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>


class SpiderTemplateError(Exception):
    pass


class SpiderDirError(Exception):
    pass


class SpiderTemplateNotFound(Exception):
    pass


class SpiderVarsFileNotFound(Exception):
    pass


class SpiderParameterError(Exception):
    pass


class SpiderVarsConfigError(Exception):
    pass
