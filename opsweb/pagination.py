from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from opsweb.exceptions import CustomException
import logging

logger = logging.getLogger(__name__)

class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        query_params = data.serializer.context.get('request').query_params
        total = self.page.paginator.count
        try:
            which_page = int(query_params.get('page')) \
                            if query_params.get('page') \
                                else 1
            page_size =  int(query_params.get('page_size')) \
                            if query_params.get('page_size') \
                                else self.page_size
        except ValueError:
            raise CustomException("Invalid query parameters.",
                                  status_code = status.HTTP_400_BAD_REQUEST)
        last_page =  total // page_size + total % page_size
        from_pos = (which_page - 1) * page_size + 1
        to_pos = which_page * page_size
        logger.debug("which_page: %s" % which_page)
        return Response({
            'total': total,
            'per_page': page_size,
            'current_page': which_page,
            'last_page': last_page,
            'next_page_url': self.get_next_link(),
            'previous_page_url': self.get_previous_link(),
            'from': from_pos,
            'to': to_pos,
            'data': data
        })
