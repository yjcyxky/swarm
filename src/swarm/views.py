import logging, json
from django.template.loader import get_template
from django.http import JsonResponse
from rest_framework.decorators import (api_view, permission_classes)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework import permissions
from swarm.permissions import IsOwnerOrAdmin

logger = logging.getLogger(__name__)


class APIDetail(APIView):
    """
    Retrieve a specified API instance.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def gen_response_obj(self, request, message=None,
                         collections=None, next=None):
        collections.update({
            "api_uri": request.get_raw_uri() if isinstance(request, Request) else None,
            "next": next
        })
        return {
            "status": message,
            "data": collections,
            "status_code": status.HTTP_200_OK
        }

    def get(self, request, api_name):
        """
        Get a specified API instance.
        ---
        The api need an `api_name` url parameter.

        api_name(Possible range of values):
            - apis
            - navbar
            - sidebar
            - welcome

        response:
            - status_code: 200
              status: "Success."
              data: {}

            - status_code: 400
              status: "Not Found."
              data: []


        status_code:
            - 200
            - 400
        """
        logger.debug('API_NAME: %s' % api_name)
        logger.debug(request.get_raw_uri())
        user = request.user
        query_params = request.query_params
        company_name = query_params.get('companyName', 'SuperSAN')
        query_arg = query_params.get('queryArg', '')

        if api_name in ('apis', 'navbar', 'sidebar', 'welcome'):
            t = get_template('%s.json.tmpl' % api_name)
            api_prefix = request.get_host()
            api_pool = t.render({
                                    "api_prefix": api_prefix,
                                    "user": user,
                                    "company_name": company_name,
                                    "query_arg": query_arg
                                })
            collections = {
                'apiData': json.loads(api_pool)
            }
            response_obj = self.gen_response_obj(request, message='Success.',
                                                 collections=collections)
            return JsonResponse(response_obj, status=200)
        else:
            return Response({
                "status": "Not Found.",
                "status_code": status.HTTP_404_NOT_FOUND,
                "data": []
            })


def custom404(request):
    return JsonResponse({
        'status_code': 404,
        'details': 'The resource was not found.',
        'status': 'Failed'
    }, status=status.HTTP_404_NOT_FOUND)
