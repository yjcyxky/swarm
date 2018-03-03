# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from account.exceptions import CustomException
import logging

logger = logging.getLogger(__name__)


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        query_params = data.serializer.context.get('request').query_params
        total = self.page.paginator.count
        try:
            which_page = int(query_params.get('page', 1))
            page_size = int(query_params.get('page_size', self.page_size))
            if page_size == 0:
                page_size = 10
        except ValueError:
            raise CustomException("Invalid query parameters.",
                                  status_code=status.HTTP_400_BAD_REQUEST)
        last_page = total // page_size + 1
        from_pos = (which_page - 1) * page_size + 1
        to_pos = (which_page * page_size if (total // page_size >= which_page)
                  else total % page_size)
        logger.debug("which_page: %s" % which_page)
        return Response({
            'total': total,
            'per_page': page_size,
            'current_page': which_page,
            'last_page': last_page,
            'next_page_url': self.get_next_link(),
            'prev_page_url': self.get_previous_link(),
            'from': from_pos,
            'to': to_pos,
            'data': data
        })
