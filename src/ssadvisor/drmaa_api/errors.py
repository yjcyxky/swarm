# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

"""
drmaa errors
"""

from ctypes import create_string_buffer

from .const import ERROR_STRING_BUFFER


class DrmaaException(Exception):

    """
    A common ancestor to all DRMAA Error classes.
    """
    pass


class AlreadyActiveSessionException(DrmaaException):
    pass


class AuthorizationException(DrmaaException):
    pass


class ConflictingAttributeValuesException(DrmaaException, AttributeError):
    pass


class DefaultContactStringException(DrmaaException):
    pass


class DeniedByDrmException(DrmaaException):
    pass


class DrmCommunicationException(DrmaaException):
    pass


class DrmsExitException(DrmaaException):
    pass


class DrmsInitException(DrmaaException):
    pass


class ExitTimeoutException(DrmaaException):
    pass


class HoldInconsistentStateException(DrmaaException):
    pass


class IllegalStateException(DrmaaException):
    pass


class InternalException(DrmaaException):
    pass


class InvalidAttributeFormatException(DrmaaException, AttributeError):
    pass


class InvalidContactStringException(DrmaaException):
    pass


class InvalidJobException(DrmaaException):
    pass


class InvalidJobTemplateException(DrmaaException):
    pass


class NoActiveSessionException(DrmaaException):
    pass


class NoDefaultContactStringSelectedException(DrmaaException):
    pass


class ReleaseInconsistentStateException(DrmaaException):
    pass


class ResumeInconsistentStateException(DrmaaException):
    pass


class SuspendInconsistentStateException(DrmaaException):
    pass


class TryLaterException(DrmaaException):
    pass


class UnsupportedAttributeException(DrmaaException, AttributeError):
    pass


class InvalidArgumentException(DrmaaException, AttributeError):
    pass


class InvalidAttributeValueException(DrmaaException, AttributeError):
    pass


class OutOfMemoryException(DrmaaException, MemoryError):
    pass

error_buffer = create_string_buffer(ERROR_STRING_BUFFER)


def error_check(code):
    if code == 0:
        return
    else:
        error_string = "code {0}: {1}".format(code, error_buffer.value.decode())
        try:
            raise _ERRORS[code - 1](error_string)
        except IndexError:
            raise DrmaaException(error_string)

# da vedere: NO_RUSAGE, NO_MORE_ELEMENTS
_ERRORS = [InternalException,
           DrmCommunicationException,
           AuthorizationException,
           InvalidArgumentException,
           NoActiveSessionException,
           OutOfMemoryException,
           InvalidContactStringException,
           DefaultContactStringException,
           NoDefaultContactStringSelectedException,
           DrmsInitException,
           AlreadyActiveSessionException,
           DrmsExitException,
           InvalidAttributeFormatException,
           InvalidAttributeValueException,
           ConflictingAttributeValuesException,
           TryLaterException,
           DeniedByDrmException,
           InvalidJobException,
           ResumeInconsistentStateException,
           SuspendInconsistentStateException,
           HoldInconsistentStateException,
           ReleaseInconsistentStateException,
           ExitTimeoutException,
           Exception,
           StopIteration]
