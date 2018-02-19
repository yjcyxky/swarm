from rest_framework.views import exception_handler
from rest_framework import status
from django.utils.encoding import force_text
from rest_framework.exceptions import APIException


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code

    return response


class CustomException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Not Found.'

    def __init__(self, detail, field=None, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        if detail is not None and field is not None:
            self.detail = {field: force_text(detail)}
        elif detail is not None:
            self.detail = {'detail': force_text(detail)}
        else:
            self.detail = {'detail': force_text(self.default_detail)}
