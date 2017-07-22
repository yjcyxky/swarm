# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import get_template
from django.apps import apps
from config import COBBLER_API_URL, INTERFACE_LANG, ZH_INTERFACE, EN_INTERFACE
from config import SSHOSTMGT_DB_SETTINGS

if INTERFACE_LANG == "en":
    INTERFACE = EN_INTERFACE
elif INTERFACE_LANG == "zh":
    INTERFACE = ZH_INTERFACE
else:
    INTERFACE = ZH_INTERFACE

apps.get_app_config("sshostmgt").db_settings = SSHOSTMGT_DB_SETTINGS
apps.get_app_config("sscobbler").settings = {
    "cobbler_api_url": COBBLER_API_URL,
    "interface_lang": INTERFACE_LANG,
    "zh_interface": ZH_INTERFACE,
    "en_interface": EN_INTERFACE
}

print(apps.get_app_config('sshostmgt').db_settings)
print(apps.get_app_config('sscobbler').settings)

def index(request):
    """
    This is the main greeting page for cobbler web.
    """
    # if not test_user_authenticated(request):
    #     return login(request, next="/sscobbler", expired=True)

    t = get_template("login.tmpl")
    html = t.render(RequestContext(request, {
        "interface": INTERFACE,
    }))
    return HttpResponse(html)