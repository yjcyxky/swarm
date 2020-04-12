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


def agent_state(request):
    MONITOR_BASE_URL = settings.MONITOR_BASE_URL
    dest_url = os.path.join(MONITOR_BASE_URL, 'master/state')
    username = settings.MONITOR_USERNAME
    password = settings.MONITOR_PASSWORD

    if username and password:
        auth = HTTPBasicAuth(username, password)
    else:
        auth = None

    try:
        r = requests.get(url=dest_url, auth = auth)
        status_code = r.status_code
        r.raise_for_status()
    except requests.RequestException as e:
        result = {
            'details': str(e),
            'status': 'Failed'
        }
    else:
        result = r.json()

    logger.info('Agent State: %s, %s, %s' % (auth, result, status_code))
    return JsonResponse(result, status=status_code)