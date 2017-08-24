# -*- coding:utf-8 -*-
import logging
from django.contrib.auth.models import User, Group

logger = logging.getLogger(__name__)

def get_results_by_page(queryset, limiting, which_page):
    """Get results by specified page.
    # Method
    # first position
        nums - (nums / limiting - which_page + 1) * limiting
    # second position
        nums - (nums / limiting - which_page) * limiting
    :param: queryset: A queryset, List
    :param: limiting: how many results in one page.
    :param: which_page: which page you want.
    :returns: return a queryset that contains results in one page which you specified
    """
    nums = len(queryset)
    if limiting > 0 and limiting <= nums \
       and which_page > 0 and which_page <= nums / limiting:
        first_pos = nums - (nums / limiting - which_page + 1) * limiting
        second_pos = nums - (nums / limiting - which_page) * limiting
        return queryset[first_pos, second_pos]
    else:
        return queryset

def get_users(filters = None, order_by = None, limiting = None, which_page = None,
              expanded = True):
    """Get information of users.
    1. You can filter results by using filter parameter.
    2. Order results by using order_by parameter.
    3. Page break by using limiting, which_page and total numbers of results.
    :param filters(Dict): A string sets for filtering results(exact matching).
    :param order_by(String): A string for ordering results, it must be a filed of Host class.
    :param limiting(Integer): A integer for specify numbers of items in one page.
    :param which_page(Integer): A integer for specify which page you want to.
    :param expanded: whether expand the query to related table.
    :returns: return a queryset that contains users you queried
    """
    order_items = ["email", "username", "first_name", "last_name"]
    filter_dict = {"email": "auth_user", "username": "auth_user", "name": "auth_group"}
    users = User.objects.select_related().all()
    # filter users
    try:
        new_users = filter_results(users, filters, filter_dict)
    except FormatError as e:
        logger.error(str(e))

    # page break
    if isinstance(limiting, int) and isinstance(which_page, int):
        new_users = get_results_by_page(new_users, limiting, which_page)

    # order results
    if isinstance(order_by, str) and order_by in order_items:
        new_users = new_users.order_by(order_by.lower())

    return [user for user in new_users.values()]
