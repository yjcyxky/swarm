# -*- coding: utf-8 -*-


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
