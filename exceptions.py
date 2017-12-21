# -*- coding: utf-8 -*-


class ScoutsException(Exception):
    pass


class ScoutsConfigException(ScoutsException):
    pass


class ScoutsSensorTimeout(ScoutsException):
    pass


class ScoutsTaskTimeout(ScoutsException):
    pass


class ScoutsSkipException(ScoutsException):
    pass
