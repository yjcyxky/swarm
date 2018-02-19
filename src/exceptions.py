# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>


class SwarmException(Exception):
    pass


class SwarmConfigException(SwarmException):
    pass


class SwarmSensorTimeout(SwarmException):
    pass


class SwarmTaskTimeout(SwarmException):
    pass


class SwarmSkipException(SwarmException):
    pass
