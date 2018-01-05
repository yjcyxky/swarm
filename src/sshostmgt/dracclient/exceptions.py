# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

class BaseClientException(Exception):

    msg_fmt = 'An unknown exception occurred'

    def __init__(self, message=None, **kwargs):
        message = self.msg_fmt % kwargs
        super(BaseClientException, self).__init__(message)


class DRACRequestFailed(BaseClientException):
    pass


class DRACOperationFailed(DRACRequestFailed):
    msg_fmt = ('DRAC operation failed. Messages: %(drac_messages)s')


class DRACUnexpectedReturnValue(DRACRequestFailed):
    msg_fmt = ('DRAC operation yielded return value %(actual_return_value)s '
               'that is neither error nor the expected '
               '%(expected_return_value)s')


class DRACEmptyResponseField(BaseClientException):
    msg_fmt = ("Attribute '%(attr)s' is not nullable, but no value received")


class DRACMissingResponseField(BaseClientException, AttributeError):
    msg_fmt = ("Attribute '%(attr)s' is missing from the response")


class InvalidParameterValue(BaseClientException):
    msg_fmt = '%(reason)s'


class WSManRequestFailure(BaseClientException):
    msg_fmt = ('WSMan request failed')


class WSManInvalidResponse(BaseClientException):
    msg_fmt = ('Invalid response received. Status code: "%(status_code)s", '
               'reason: "%(reason)s"')


class WSManInvalidFilterDialect(BaseClientException):
    msg_fmt = ('Invalid filter dialect "%(invalid_filter)s". '
               'Supported options are %(supported)s')
