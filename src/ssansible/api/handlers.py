import logging
import sys
import traceback
from django.core.exceptions import PermissionDenied

from django.core import exceptions as djexcs
from rest_framework import exceptions, status, views
from rest_framework.response import Response

from ..main import exceptions as mexcs

logger = logging.getLogger("ssansible")


def polemarch_exception_handler(exc, context):
    # pylint: disable=too-many-return-statements
    logger.info(traceback.format_exc())
    default_exc = (exceptions.APIException, djexcs.PermissionDenied)

    if isinstance(exc, PermissionDenied):  # pragma: no cover
        return Response({"detail": str(exc)},
                        status=status.HTTP_403_FORBIDDEN)

    elif isinstance(exc, mexcs.DataNotReady):
        return Response({"detail": exc.msg},
                        status=status.HTTP_424_FAILED_DEPENDENCY)

    elif isinstance(exc, mexcs.NotApplicable):
        return Response({"detail": exc.msg},
                        status=status.HTTP_404_NOT_FOUND)

    elif isinstance(exc, djexcs.ValidationError):
        if hasattr(exc, 'error_dict'):
            errors = dict(exc)
        elif hasattr(exc, 'error_list'):
            errors =  {'other_errors': list(exc)}
        else:
            errors = {'other_errors': str(exc)}
        return Response({"detail": errors},
                        status=status.HTTP_400_BAD_REQUEST)

    elif isinstance(exc, mexcs.UnknownTypeException):
        return Response({"detail": exc.msg},
                        status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    elif not isinstance(exc, default_exc) and isinstance(exc, Exception):
        return Response({'detail': str(sys.exc_info()[1]),
                         'error_type': sys.exc_info()[0].__name__},
                        status=status.HTTP_400_BAD_REQUEST)

    default_response = views.exception_handler(exc, context)

    if isinstance(exc, exceptions.NotAuthenticated):
        default_response["X-Anonymous"] = "true"

    return default_response
