import os
import requests
import logging
from requests.auth import HTTPBasicAuth
from django.http import JsonResponse
from rest_framework import status
from swarm import settings
from swarm.version import get_version as version

logger = logging.getLogger('swarm')

def custom404(request):
    return JsonResponse({
        'status_code': 404,
        'details': 'The resource was not found.',
        'status': 'Failed'
    }, status=status.HTTP_404_NOT_FOUND)


def get_version(request):
    return JsonResponse({
        'version': version()
    }, status=status.HTTP_200_OK)
