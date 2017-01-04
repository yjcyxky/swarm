# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import get_template

from sscop_config import COBBLER_API_URL, INTERFACE_LANG, ZH_INTERFACE, EN_INTERFACE
if INTERFACE_LANG == 'en':
    INTERFACE = EN_INTERFACE
elif INTERFACE_LANG == 'zh':
    INTERFACE = ZH_INTERFACE
else:
    INTERFACE = ZH_INTERFACE

def index(request):
    """
    This is the main greeting page for cobbler web.
    """
    # if not test_user_authenticated(request):
    #     return login(request, next="/sscobbler", expired=True)

    t = get_template('index.tmpl')
    html = t.render(RequestContext(request, {
        'interface': INTERFACE,
    }))
    return HttpResponse(html)