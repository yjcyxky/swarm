# -*- coding: utf-8 -*-
from django.http import HttpResponse, JsonResponse, HttpRequest
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.shortcuts import render
from django.template import RequestContext
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.apps import apps

import simplejson
import string
import time
import xmlrpclib

import field_ui_info

sscobbler_settings = apps.get_app_config("sscobbler").settings
COBBLER_API_URL = sscobbler_settings.get("cobbler_api_url")
INTERFACE_LANG = sscobbler_settings.get("interface_lang")
ZH_INTERFACE = sscobbler_settings.get("zh_interface")
EN_INTERFACE = sscobbler_settings.get("en_interface")

url_cobbler_api = None
remote = None
username = None

if INTERFACE_LANG == 'en':
    INTERFACE = EN_INTERFACE
elif INTERFACE_LANG == 'zh':
    INTERFACE = ZH_INTERFACE
else:
    INTERFACE = ZH_INTERFACE

# ==================================================================================

def gen_response_obj(request, message = None, collections = None, next = None):
    return {
        "message": message or "Method Not Allowed.",
        "collections": collections,
        "api_uri": request.get_raw_uri() if isinstance(request, HttpRequest) else None,
        "next": next
    }

def local_get_cobbler_api_url():
    return COBBLER_API_URL

def strip_none(data, omit_none=False):
    """
    Remove "none" entries from datastructures.
    Used prior to communicating with XMLRPC.
    """
    if data is None:
        data = '~'

    elif isinstance(data, list):
        data2 = []
        for x in data:
            if omit_none and x is None:
                pass
            else:
                data2.append(strip_none(x))
        return data2

    elif isinstance(data, dict):
        data2 = {}
        for key in data.keys():
            if omit_none and data[key] is None:
                pass
            else:
                data2[str(key)] = strip_none(data[key])
        return data2

    return data

@login_required(login_url='/login/')
def index(request):
    """
    This is the main greeting page for cobbler web.
    """
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler", expired=True)

    response_obj = gen_response_obj(request)
    if request.method == "GET":
        json = {
            'status': 'OK',
            'message': 'sscobbler is alive.',
            'collections': {
                'sscobbler': {
                    # 调用cobbler API获取(可修改/etc/cobbler/version文件或SSCOPDeploy项目setup.py文件)
                    'version': remote.extended_version(request.session['token'])['version'],
                }
            },
            'url': request.get_full_path()
        }
        return JsonResponse(json, status = 200)
    else:
        return JsonResponse(response_obj, status = 405)

# ========================================================================

def task_created(request):
    """
    Let's the user know what to expect for event updates.
    """
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/task_created", expired=True)

    response_obj = gen_response_obj(request)
    if request.method == "GET":
        t = get_template("task_created.tmpl")
        html = t.render(RequestContext(request, {
            'interface': INTERFACE,
            'version': remote.extended_version(request.session['token'])['version'],
            'username': username
        }))
        response_obj["message"] = "success.",
        response_obj["collections"] = {"task_created": html}
        return JsonResponse(response_obj, status = 200)
    else:
        return JsonResponse(response_obj, status = 405)

# ========================================================================

def error_page(request, message):
    """
    This page is used to explain error messages to the user.
    """
    if not test_user_authenticated(request):
        return login(request, expired=True)
    # FIXME: test and make sure we use this rather than throwing lots of tracebacks for
    # field errors
    response_obj = gen_response_obj(request)
    if request.method == "GET":
        t = get_template('error_page.tmpl')
        message = message.replace("<Fault 1: \"<class 'cobbler.cexceptions.CX'>:'", "Remote exception: ")
        message = message.replace("'\">", "")
        html = t.render(RequestContext(request, {
            'interface': INTERFACE,
            'version': remote.extended_version(request.session['token'])['version'],
            'message': message,
            'username': username
        }))

        response_obj["message"] = "success.",
        response_obj["collections"] = {"error_page": html}
        return JsonResponse(response_obj, status = 200)
    else:
        return JsonResponse(response_obj, status = 405)

# ==================================================================================

def _get_field_html_element(field_name):

    if field_name in field_ui_info.USES_SELECT:
        return "select"
    elif field_name in field_ui_info.USES_MULTI_SELECT:
        return "multiselect"
    elif field_name in field_ui_info.USES_RADIO:
        return "radio"
    elif field_name in field_ui_info.USES_CHECKBOX:
        return "checkbox"
    elif field_name in field_ui_info.USES_TEXTAREA:
        return "textarea"
    else:
        return "text"


def get_fields(what, is_subobject, seed_item=None):

    """
    Helper function.  Retrieves the field table from the cobbler objects
    and formats it in a way to make it useful for Django templating.
    The field structure indicates what fields to display and what the default
    values are, etc.
    """

    if what == "distro":
        fields = remote.get_item_distro_fileds()
    if what == "profile":
        fields = remote.get_item_profile_fileds()
    if what == "system":
        fields = remote.get_item_system_fileds()
    if what == "repo":
        fields = remote.get_item_repo_fileds()
    if what == "image":
        fields = remote.get_item_image_fileds()
    if what == "mgmtclass":
        fields = remote.get_item_mgmtclass_fileds()
    if what == "package":
        fields = remote.get_item_package_fileds()
    if what == "file":
        fields = remote.get_item_file_fileds()
    if what == "setting":
        fields = remote.get_item_settings_fileds()

    settings = remote.get_settings()

    ui_fields = []
    for field in fields:

        ui_field = {
            "name": field[0],
            "dname": field[0],
            "value": "?",
            "caption": field[3],
            "editable": field[4],
            "tooltip": field[5],
            "choices": field[6],
            "css_class": "generic",
            "html_ui_fieldent": "generic",
        }

        if not ui_field["editable"]:
            continue

        name = field[0]
        if seed_item is not None:
            ui_field["value"] = seed_item[name]
        elif is_subobject:
            ui_field["value"] = field[2]
        else:
            ui_field["value"] = field[1]

        if ui_field["value"] is None:
            ui_field["value"] = ""

        # we'll process this for display but still need to present the original to some
        # template logic
        ui_field["value_raw"] = ui_field["value"]

        if isinstance(ui_field["value"], basestring) and ui_field["value"].startswith("SETTINGS:"):
            key = ui_field["value"].replace("SETTINGS:", "", 1)
            ui_field["value"] = settings[key]

        # flatten dicts of all types, they can only be edited as text
        # as we have no HTML dict widget (yet)
        if isinstance(ui_field["value"], dict):
            if ui_field["name"] == "mgmt_parameters":
                # Render dictionary as YAML for Management Parameters field
                tokens = []
                for (x, y) in ui_field["value"].items():
                    if y is not None:
                        tokens.append("%s: %s" % (x, y))
                    else:
                        tokens.append("%s: " % x)
                ui_field["value"] = "{ %s }" % ", ".join(tokens)
            else:
                tokens = []
                for (x, y) in ui_field["value"].items():
                    if isinstance(y, basestring) and y.strip() != "~":
                        y = y.replace(" ", "\\ ")
                        tokens.append("%s=%s" % (x, y))
                    elif isinstance(y, list):
                        for l in y:
                            l = l.replace(" ", "\\ ")
                            tokens.append("%s=%s" % (x, l))
                    elif y is not None:
                        tokens.append("%s" % x)
                ui_field["value"] = " ".join(tokens)

        name = field[0]
        ui_field["html_element"] = _get_field_html_element(name)

        # flatten lists for those that aren't using select boxes
        if isinstance(ui_field["value"], list):
            if ui_field["html_element"] != "select":
                ui_field["value"] = string.join(ui_field["value"], sep=" ")

        ui_fields.append(ui_field)

    return ui_fields


def get_network_interface_fields():
    """
    Create network interface fields UI metadata based on network interface
    fields metadata

    @return list network interface fields UI metadata
    """

    fields = remote.get_network_interface_fields()

    fields_ui = []
    for field in fields:

        field_ui = {
            "name": field[0],
            "dname": field[0],
            "value": "?",
            "caption": field[3],
            "editable": field[4],
            "tooltip": field[5],
            "choices": field[6],
            "css_class": "generic",
            "html_element": "generic",
        }

        if not field_ui["editable"]:
            continue

        # system's network interfaces are loaded later by javascript,
        # initial value on web UI is always empty string
        field_ui["value"] = ""

        # we'll process this for display but still need to present the original
        # to some template logic
        field_ui["value_raw"] = field_ui["value"]

        name = field[0]
        field_ui["html_element"] = _get_field_html_element(name)

        fields_ui.append(field_ui)

    return fields_ui


def _create_sections_metadata(what, sections_data, fields):

    sections = {}
    section_index = 0
    for section_data in sections_data:
        for section_name, section_fields in section_data.items():
            skey = "%d_%s" % (section_index, section_name)
            sections[skey] = {}
            sections[skey]['name'] = section_name
            sections[skey]['fields'] = []

            for section_field in section_fields:
                found = False
                for field in fields:
                    if field["name"] == section_field:
                        sections[skey]['fields'].append(field)
                        found = True
                        break
                if not found:
                    raise Exception("%s field %s referenced in UI section definition does not exist in UI fields definition" % (what, section_field))

            section_index += 1

    return sections

# ==================================================================================

def __tweak_field(fields, field_name, attribute, value):
    """
    Helper function to insert extra data into the field list.
    """
    # FIXME: eliminate this function.
    for x in fields:
        if x["name"] == field_name:
            x[attribute] = value

# ==================================================================================

def __format_columns(column_names, sort_field):
    """
    Format items retrieved from XMLRPC for rendering by the generic_edit template
    """
    dataset = []

    # Default is sorting on name
    if sort_field is not None:
        sort_name = sort_field
    else:
        sort_name = "name"

    if sort_name.startswith("!"):
        sort_name = sort_name[1:]
        sort_order = "desc"
    else:
        sort_order = "asc"

    for fieldname in column_names:
        fieldorder = "none"
        if fieldname == sort_name:
            fieldorder = sort_order
        dataset.append([fieldname, fieldorder])
    return dataset


# ==================================================================================

def __format_items(items, column_names):
    """
    Format items retrieved from XMLRPC for rendering by the generic_edit template
    """
    dataset = []
    for item_dict in items:
        row = []
        for fieldname in column_names:
            if fieldname == "name":
                html_element = "name"
            elif fieldname in ["system", "repo", "distro", "profile", "image", "mgmtclass", "package", "file"]:
                html_element = "editlink"
            elif fieldname in field_ui_info.USES_CHECKBOX:
                html_element = "checkbox"
            else:
                html_element = "text"
            row.append([fieldname, item_dict[fieldname], html_element])
        dataset.append(row)
    return dataset

# ==================================================================================

def genlist(request, what, page=None):
    """
    Lists all object types, complete with links to actions
    on those objects.
    """
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/%s/list" % what, expired=True)

    response_obj = gen_response_obj(request)
    if request.method == "GET":
        # get details from the session
        if page is None:
            page = int(request.session.get("%s_page" % what, 1))
        limit = int(request.session.get("%s_limit" % what, 50))
        sort_field = request.session.get("%s_sort_field" % what, "name")
        filters = simplejson.loads(request.session.get("%s_filters" % what, "{}"))
        pageditems = remote.find_items_paged(what, strip_none(filters), sort_field, page, limit)

        # what columns to show for each page?
        # we also setup the batch actions here since they're dependent
        # on what we're looking at

        profiles = []

        # everythng gets batch delete
        batchactions = [
            ["Delete", "delete", "delete"],
        ]

        if what == "distro":
            columns = ["name"]
            batchactions += [
                ["Build ISO", "buildiso", "enable"],
            ]
        if what == "profile":
            columns = ["name", "distro"]
            batchactions += [
                ["Build ISO", "buildiso", "enable"],
            ]
        if what == "system":
            # FIXME: also list network, once working
            columns = ["name", "profile", "status", "netboot_enabled"]
            profiles = sorted(remote.get_profiles())
            batchactions += [
                ["Power on", "power", "on"],
                ["Power off", "power", "off"],
                ["Reboot", "power", "reboot"],
                ["Change profile", "profile", ""],
                ["Netboot enable", "netboot", "enable"],
                ["Netboot disable", "netboot", "disable"],
                ["Build ISO", "buildiso", "enable"],
            ]
        if what == "repo":
            columns = ["name", "mirror"]
            batchactions += [
                ["Reposync", "reposync", "go"],
            ]
        if what == "image":
            columns = ["name", "file"]
        if what == "network":
            columns = ["name"]
        if what == "mgmtclass":
            columns = ["name"]
        if what == "package":
            columns = ["name", "installer"]
        if what == "file":
            columns = ["name"]

        # render the list
        t = get_template('generic_list.tmpl')
        html = t.render(RequestContext(request, {
            'what': what,
            'columns': __format_columns(columns, sort_field),
            'items': __format_items(pageditems["items"], columns),
            'pageinfo': pageditems["pageinfo"],
            'filters': filters,
            'interface': INTERFACE,
            'version': remote.extended_version(request.session['token'])['version'],
            'username': username,
            'limit': limit,
            'batchactions': batchactions,
            'profiles': profiles,
        }))

        response_obj["message"] = "success.",
        response_obj["collections"] = {"genlist": html}
        return JsonResponse(response_obj, status = 200)
    else:
        return JsonResponse(response_obj, status = 405)


# @require_POST
def modify_list(request, what, pref, value=None):
    """
    This function is used in the generic list view
    to modify the page/column sort/number of items
    shown per page, and also modify the filters.

    This function modifies the session object to
    store these preferences persistently.
    """
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/%s/modifylist/%s/%s" % (what, pref, str(value)), expired=True)

    # what preference are we tweaking?
    if request.method == "POST":
        if pref == "sort":

            # FIXME: this isn't exposed in the UI.

            # sorting list on columns
            old_sort = request.session.get("%s_sort_field" % what, "name")
            if old_sort.startswith("!"):
                old_sort = old_sort[1:]
                old_revsort = True
            else:
                old_revsort = False
            # User clicked on the column already sorted on,
            # so reverse the sorting list
            if old_sort == value and not old_revsort:
                value = "!" + value
            request.session["%s_sort_field" % what] = value
            request.session["%s_page" % what] = 1

        elif pref == "limit":
            # number of items to show per page
            request.session["%s_limit" % what] = int(value)
            request.session["%s_page" % what] = 1

        elif pref == "page":
            # what page are we currently on
            request.session["%s_page" % what] = int(value)

        elif pref in ("addfilter", "removefilter"):
            # filters limit what we show in the lists
            # they are stored in json format for marshalling
            filters = simplejson.loads(request.session.get("%s_filters" % what, "{}"))
            if pref == "addfilter":
                (field_name, field_value) = value.split(":", 1)
                # add this filter
                filters[field_name] = field_value
            else:
                # remove this filter, if it exists
                if value in filters:
                    del filters[value]
            # save session variable
            request.session["%s_filters" % what] = simplejson.dumps(filters)
            # since we changed what is viewed, reset the page
            request.session["%s_page" % what] = 1

        else:
            return error_page(request, "Invalid preference change request")

        # redirect to the list page
        # return HttpResponseRedirect("/sscobbler/%s/list" % what)
        url = '/sscobbler/%s/list' % what
        return JsonResponse({'status': True, 'message': None, 'url': url}, status = 200)
    else:
        return JsonResponse(gen_response_obj(request), status = 405)

# ======================================================================

# @require_POST
def generic_rename(request, what, obj_name=None, obj_newname=None):
    """
    Renames an object.
    """
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/%s/rename/%s/%s" % (what, obj_name, obj_newname), expired=True)

    if request.method == "POST":
        if obj_name is None:
            return error_page(request, "You must specify a %s to rename" % what)
        if not remote.has_item(what, obj_name):
            return error_page(request, "Unknown %s specified" % what)
        elif not remote.check_access_no_fail(request.session['token'], "modify_%s" % what, obj_name):
            return error_page(request, "You do not have permission to rename this %s" % what)
        else:
            obj_id = remote.get_item_handle(what, obj_name, request.session['token'])
            remote.rename_item(what, obj_id, obj_newname, request.session['token'])
            # return HttpResponseRedirect("/sscobbler/%s/list" % what)
            url = '/sscobbler/%s/list' % what
            return JsonResponse({'status': True, 'message': None, 'url': url})
    else:
        return JsonResponse(gen_response_obj(request), status = 405)

# ======================================================================

# @require_POST
def generic_copy(request, what, obj_name=None, obj_newname=None):
    """
    Copies an object.
    """
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/%s/copy/%s/%s" % (what, obj_name, obj_newname), expired=True)
    # FIXME: shares all but one line with rename, merge it.

    if request.method == "POST":
        if obj_name is None:
            return error_page(request, "You must specify a %s to rename" % what)
        if not remote.has_item(what, obj_name):
            return error_page(request, "Unknown %s specified" % what)
        elif not remote.check_access_no_fail(request.session['token'], "modify_%s" % what, obj_name):
            return error_page(request, "You do not have permission to copy this %s" % what)
        else:
            obj_id = remote.get_item_handle(what, obj_name, request.session['token'])
            remote.copy_item(what, obj_id, obj_newname, request.session['token'])
            # return HttpResponseRedirect("/sscobbler/%s/list" % what)
            url = '/sscobbler/%s/list' % what
            return JsonResponse({'status': True, 'message': None, 'url': url})
    else:
        return JsonResponse(gen_response_obj(request), status = 405)

# ======================================================================

# @require_POST
def generic_delete(request, what, obj_name=None):
    """
    Deletes an object.
    """
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/%s/delete/%s" % (what, obj_name), expired=True)
    # FIXME: consolidate code with above functions.

    if request.method == "POST":
        if obj_name is None:
            return error_page(request, "You must specify a %s to delete" % what)
        if not remote.has_item(what, obj_name):
            return error_page(request, "Unknown %s specified" % what)
        elif not remote.check_access_no_fail(request.session['token'], "remove_%s" % what, obj_name):
            return error_page(request, "You do not have permission to delete this %s" % what)
        else:
            # check whether object is to be deleted recursively
            recursive = simplejson.loads(request.POST.get("recursive", "false"))
            try:
                remote.xapi_object_edit(what, obj_name, "remove", {'name': obj_name, 'recursive': recursive}, request.session['token'])
            except Exception, e:
                return error_page(request, str(e))
            # return HttpResponseRedirect("/sscobbler/%s/list" % what)
            url = '/sscobbler/%s/list' % what
            return JsonResponse({'status': True, 'message': None, 'url': url})
    else:
        return JsonResponse(gen_response_obj(request), status = 405)

# ======================================================================

# @require_POST
def generic_domulti(request, what, multi_mode=None, multi_arg=None):
    """
    Process operations like profile reassignment, netboot toggling, and deletion
    which occur on all items that are checked on the list page.
    """
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/%s/multi/%s/%s" % (what, multi_mode, multi_arg), expired=True)

    if request.method == "POST":
        names = request.POST.get('names', '').strip().split()
        if names == "":
            return error_page(request, "Need to select some '%s' objects first" % what)

        if multi_mode == "delete":
            # check whether the objects are to be deleted recursively
            recursive = simplejson.loads(request.POST.get("recursive_batch", "false"))
            for obj_name in names:
                try:
                    remote.xapi_object_edit(what, obj_name, "remove", {'name': obj_name, 'recursive': recursive}, request.session['token'])
                except Exception, e:
                    return error_page(request, str(e))

        elif what == "system" and multi_mode == "netboot":
            netboot_enabled = multi_arg  # values: enable or disable
            if netboot_enabled is None:
                return error_page(request, "Cannot modify systems without specifying netboot_enabled")
            if netboot_enabled == "enable":
                netboot_enabled = True
            elif netboot_enabled == "disable":
                netboot_enabled = False
            else:
                return error_page(request, "Invalid netboot option, expect enable or disable")
            for obj_name in names:
                obj_id = remote.get_system_handle(obj_name, request.session['token'])
                remote.modify_system(obj_id, "netboot_enabled", netboot_enabled, request.session['token'])
                remote.save_system(obj_id, request.session['token'], "edit")

        elif what == "system" and multi_mode == "profile":
            profile = multi_arg
            if profile is None:
                return error_page(request, "Cannot modify systems without specifying profile")
            for obj_name in names:
                obj_id = remote.get_system_handle(obj_name, request.session['token'])
                remote.modify_system(obj_id, "profile", profile, request.session['token'])
                remote.save_system(obj_id, request.session['token'], "edit")

        elif what == "system" and multi_mode == "power":
            power = multi_arg
            if power is None:
                return error_page(request, "Cannot modify systems without specifying power option")
            options = {"systems": names, "power": power}
            remote.background_power_system(options, request.session['token'])

        elif what == "system" and multi_mode == "buildiso":
            options = {"systems": names, "profiles": []}
            remote.background_buildiso(options, request.session['token'])

        elif what == "profile" and multi_mode == "buildiso":
            options = {"profiles": names, "systems": []}
            remote.background_buildiso(options, request.session['token'])

        elif what == "distro" and multi_mode == "buildiso":
            if len(names) > 1:
                return error_page(request, "You can only select one distro at a time to build an ISO for")
            options = {"standalone": True, "distro": str(names[0])}
            remote.background_buildiso(options, request.session['token'])

        elif what == "repo" and multi_mode == "reposync":
            options = {"repos": names, "tries": 3}
            remote.background_reposync(options, request.session['token'])

        else:
            return error_page(request, "Unknown batch operation on %ss: %s" % (what, str(multi_mode)))

        # FIXME: "operation complete" would make a lot more sense here than a redirect
        # return HttpResponseRedirect("/sscobbler/%s/list" % what)
        url = '/sscobbler/%s/list' % what
        return JsonResponse({'status': True, 'message': None, 'url': url})
    else:
        return JsonResponse(gen_response_obj(request), status = 405)

# ======================================================================

def import_prompt(request):
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/import/prompt", expired=True)

    response_obj = gen_response_obj(request)
    if request.method == "GET":
        t = get_template('import.tmpl')
        html = t.render(RequestContext(request, {
            'interface': INTERFACE,
            'version': remote.extended_version(request.session['token'])['version'],
            'username': username,
        }))

        response_obj["message"] = "success.",
        response_obj["collections"] = {"import_prompt": html}
        return JsonResponse(response_obj, status = 200)
    else:
        return JsonResponse(response_obj, status = 405)

# ======================================================================

def check(request):
    """
    Shows a page with the results of 'cobbler check'
    """
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/check", expired=True)

    response_obj = gen_response_obj(request)
    if request.method == "GET":
        results = remote.check(request.session['token'])
        t = get_template('check.tmpl')
        html = t.render(RequestContext(request, {
            'interface': INTERFACE,
            'version': remote.extended_version(request.session['token'])['version'],
            'username': username,
            'results': results
        }))

        response_obj["message"] = "success.",
        response_obj["collections"] = {"check": html}
        return JsonResponse(response_obj, status = 200)
    else:
        return JsonResponse(response_obj, status = 405)

# ======================================================================

# @require_POST
def buildiso(request):
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/buildiso", expired=True)

    if request.method == "POST":
        remote.background_buildiso({}, request.session['token'])
        return HttpResponseRedirect('/sscobbler/task_created')
    else:
        return JsonResponse(gen_response_obj(request), status = 405)

# ======================================================================

# @require_POST
def import_run(request):
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/import/prompt", expired=True)

    if request.method == "POST":
        options = {
            "name": request.POST.get("name", ""),
            "path": request.POST.get("path", ""),
            "breed": request.POST.get("breed", ""),
            "arch": request.POST.get("arch", "")
        }
        remote.background_import(options, request.session['token'])
        return HttpResponseRedirect('/sscobbler/task_created')
    else:
        return JsonResponse(gen_response_obj(request), status = 405)

# ======================================================================

def aifile_list(request, page=None):
    """
    List all automatic OS installation templates and link to their edit pages.
    """
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/aifile/list", expired=True)

    response_obj = gen_response_obj(request)
    if request.method == "GET":
        aifiles = remote.get_autoinstall_templates(request.session['token'])

        aifile_list = []
        for aifile in aifiles:
            aifile_list.append((aifile, 'editable'))

        t = get_template('aifile_list.tmpl')
        html = t.render(RequestContext(request, {
            'what': 'aifile',
            'ai_files': aifile_list,
            'interface': INTERFACE,
            'version': remote.extended_version(request.session['token'])['version'],
            'username': username,
            'item_count': len(aifile_list[0]),
        }))

        response_obj["message"] = "success.",
        response_obj["collections"] = {"aifile_list": html}
        return JsonResponse(response_obj, status = 200)
    else:
        return JsonResponse(response_obj, status = 405)

# ======================================================================

def aifile_edit(request, aifile_name=None, editmode='edit'):
    """
    This is the page where an automatic OS installation file is edited.
    """
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/aifile/edit/file:%s" % aifile_name, expired=True)

    response_obj = gen_response_obj(request)
    if request.method == "GET":
        if editmode == 'edit':
            editable = False
        else:
            editable = True
        deleteable = False
        aidata = ""
        if aifile_name is not None:
            editable = remote.check_access_no_fail(request.session['token'], "modify_autoinst", aifile_name)
            deleteable = not remote.is_autoinstall_in_use(aifile_name, request.session['token'])
            aidata = remote.read_autoinstall_template(aifile_name, request.session['token'])

        t = get_template('aifile_edit.tmpl')
        html = t.render(RequestContext(request, {
            'aifile_name': aifile_name,
            'deleteable': deleteable,
            'aidata': aidata,
            'editable': editable,
            'editmode': editmode,
            'interface': INTERFACE,
            'version': remote.extended_version(request.session['token'])['version'],
            'username': username
        }))

        response_obj["message"] = "success.",
        response_obj["collections"] = {"aifile_edit": html}
        return JsonResponse(response_obj, status = 200)
    else:
        return JsonResponse(response_obj, status = 405)

# ======================================================================

# @require_POST
def aifile_save(request):
    """
    This page processes and saves edits to an automatic OS installation file.
    """
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/aifile/list", expired=True)
    # FIXME: error checking

    if request.method == "POST":
        aifile_name = request.POST.get('aifile_name', None)
        aidata = request.POST.get('aidata', "").replace('\r\n', '\n')

        if aifile_name is None:
            return HttpResponse("NO AUTOMATIC INSTALLATION FILE NAME SPECIFIED")

        delete1 = request.POST.get('delete1', None)
        delete2 = request.POST.get('delete2', None)

        if delete1 and delete2:
            remote.remove_autoinstall_template(aifile_name, request.session['token'])
            # return HttpResponseRedirect('/sscobbler/aifile/list')
            return JsonResponse({'status': True, 'message': None, 'url': '/sscobbler/aifile/list'})
        else:
            remote.write_autoinstall_template(aifile_name, aidata, request.session['token'])
            # return HttpResponseRedirect('/sscobbler/aifile/list')
            return JsonResponse({'status': True, 'message': None, 'url': '/sscobbler/aifile/list'})
    else:
        return JsonResponse(gen_response_obj(request), status = 405)

# ======================================================================

def snippet_list(request, page=None):
    """
    This page lists all available snippets and has links to edit them.
    """
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/snippet/list", expired=True)

    response_obj = gen_response_obj(request)
    if request.method == "GET":
        snippets = remote.get_autoinstall_snippets(request.session['token'])
        snippet_list = []
        for snippet in snippets:
            snippet_list.append((snippet, 'editable'))

        t = get_template('snippet_list.tmpl')
        html = t.render(RequestContext(request, {
            'what': 'snippet',
            'snippets': snippet_list,
            'interface': INTERFACE,
            'version': remote.extended_version(request.session['token'])['version'],
            'username': username
        }))

        response_obj["message"] = "success.",
        response_obj["collections"] = {"snippet_list": html}
        return JsonResponse(response_obj, status = 200)
    else:
        return JsonResponse(response_obj, status = 405)

# ======================================================================

def snippet_edit(request, snippet_name=None, editmode='edit'):
    """
    This page edits a specific snippet.
    """
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/edit/file:%s" % snippet_name, expired=True)

    response_obj = gen_response_obj(request)
    if request.method == "GET":
        if editmode == 'edit':
            editable = False
        else:
            editable = True
        deleteable = False
        snippetdata = ""
        if snippet_name is not None:
            editable = remote.check_access_no_fail(request.session['token'], "modify_snippet", snippet_name)
            deleteable = True
            snippetdata = remote.read_autoinstall_snippet(snippet_name, request.session['token'])

        t = get_template('snippet_edit.tmpl')
        html = t.render(RequestContext(request, {
            'snippet_name': snippet_name,
            'deleteable': deleteable,
            'snippetdata': snippetdata,
            'editable': editable,
            'editmode': editmode,
            'interface': INTERFACE,
            'version': remote.extended_version(request.session['token'])['version'],
            'username': username
        }))

        response_obj["message"] = "success.",
        response_obj["collections"] = {"snippet_edit": html}
        return JsonResponse(response_obj, status = 200)
    else:
        return JsonResponse(response_obj, status = 405)

# ======================================================================

# @require_POST
def snippet_save(request):
    """
    This snippet saves a snippet once edited.
    """
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/snippet/list", expired=True)
    # FIXME: error checking

    if request.method == "POST":
        editmode = request.POST.get('editmode', 'edit')
        snippet_name = request.POST.get('snippet_name', None)
        snippetdata = request.POST.get('snippetdata', "").replace('\r\n', '\n')

        if snippet_name is None:
            # return HttpResponse("NO SNIPPET NAME SPECIFIED")
            return JsonResponse({'status': False, 'message': INTERFACE.no_snippet_wmsg, 'url': None})

        if editmode != 'edit':
            if snippet_name.find("/var/lib/cobbler/snippets/") != 0:
                snippet_name = "/var/lib/cobbler/snippets/" + snippet_name

        delete1 = request.POST.get('delete1', None)
        delete2 = request.POST.get('delete2', None)

        if delete1 and delete2:
            remote.remove_autoinstall_snippet(snippet_name, request.session['token'])
            # return HttpResponseRedirect('/sscobbler/snippet/list')
            return JsonResponse({'status': True, 'message': None, 'url': '/sscobbler/snippet/list'})
        else:
            remote.write_autoinstall_snippet(snippet_name, snippetdata, request.session['token'])
            # return HttpResponseRedirect('/sscobbler/snippet/list')
            return JsonResponse({'status': True, 'message': None, 'url': '/sscobbler/snippet/list'})
    else:
        return JsonResponse(gen_response_obj(request), status = 405)

# ======================================================================

def setting_list(request):
    """
    This page presents a list of all the settings to the user.  They are not editable.
    """
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/setting/list", expired=True)

    if request.method == "GET":
        settings = remote.get_settings()
        skeys = settings.keys()
        skeys.sort()

        results = []
        for k in skeys:
            results.append([k, settings[k]])

        t = get_template('settings.tmpl')
        html = t.render(RequestContext(request, {
            'settings': results,
            'interface': INTERFACE,
            'version': remote.extended_version(request.session['token'])['version'],
            'username': username,
        }))
        response_obj = gen_response_obj(request,
                                        message = "success.",
                                        collections = {
                                            "setting_list": html
                                        })
        return JsonResponse(response_obj, status = 200)
    else:
        return JsonResponse(gen_response_obj(request), status = 405)


def setting_edit(request, setting_name=None):
    response_obj = gen_response_obj(request)
    if request.method == "GET":
        if not setting_name:
            # return HttpResponseRedirect('/sscobbler/setting/list')
            return JsonResponse({'status': False, 'message': None, 'url': '/sscobbler/setting/list'})
        if not test_user_authenticated(request):
            return login(request, next="/sscobbler/setting/edit/%s" % setting_name, expired=True)

        settings = remote.get_settings()
        if setting_name not in settings:
            return error_page(request, "Unknown setting: %s" % setting_name)

        cur_setting = {
            'name': setting_name,
            'value': settings[setting_name],
        }

        fields = get_fields('setting', False, seed_item=cur_setting)

        # build UI tabs metadata
        sections_data = field_ui_info.SETTING_UI_FIELDS_MAPPING
        sections = _create_sections_metadata('setting', sections_data, fields)

        t = get_template('generic_edit.tmpl')
        html = t.render(RequestContext(request, {
            'what': 'setting',
            'sections': sections,
            'subobject': False,
            'editmode': 'edit',
            'editable': True,
            'interface': INTERFACE,
            'version': remote.extended_version(request.session['token'])['version'],
            'username': username,
            'name': setting_name,
        }))

        response_obj["message"] = "success.",
        response_obj["collections"] = {"setting_edit": html}
        return JsonResponse(response_obj, status = 200)
    else:
        return JsonResponse(response_obj, status = 405)


def setting_save(request):
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/setting/list", expired=True)

    if request.method == "POST":
        # load request fields and see if they are valid
        setting_name = request.POST.get('name', "")
        setting_value = request.POST.get('value', None)

        if setting_name == "":
            return error_page(request, "The setting name was not specified")

        settings = remote.get_settings()
        if setting_name not in settings:
            return error_page(request, "Unknown setting: %s" % setting_name)

        if remote.modify_setting(setting_name, setting_value, request.session['token']):
            return error_page(request, "There was an error saving the setting")

        # return HttpResponseRedirect("/sscobbler/setting/list")
        return JsonResponse({'status': True, 'message': None, 'url': '/sscobbler/setting/list'})
    else:
        return JsonResponse(gen_response_obj(request), status = 405)

# ======================================================================

def events(request):
    """
    This page presents a list of all the events and links to the event log viewer.
    """
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/events", expired=True)

    response_obj = gen_response_obj(request)
    if request.method == "GET":
        events = remote.get_events()

        events2 = []
        for id in events.keys():
            (ttime, name, state, read_by) = events[id]
            events2.append([id, time.asctime(time.localtime(ttime)), name, state])

        def sorter(a, b):
            return cmp(a[0], b[0])
        events2.sort(sorter)

        t = get_template('events.tmpl')
        html = t.render(RequestContext(request, {
            'results': events2,
            'interface': INTERFACE,
            'version': remote.extended_version(request.session['token'])['version'],
            'username': username
        }))

        response_obj["message"] = "success.",
        response_obj["collections"] = {"events": html}
        return JsonResponse(response_obj, status = 200)
    else:
        return JsonResponse(response_obj, status = 405)

# ======================================================================

def eventlog(request, event=0):
    """
    Shows the log for a given event.
    """
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/eventlog/%s" % str(event), expired=True)

    response_obj = gen_response_obj(request)
    if request.method == "GET":
        event_info = remote.get_events()
        if event not in event_info:
            return JsonResponse(gen_response_obj(request, message = "Not Found."))

        data = event_info[event]
        eventname = data[0]
        eventtime = data[1]
        eventstate = data[2]
        eventlog = remote.get_event_log(event)

        t = get_template('eventlog.tmpl')
        vars = {
            'eventlog': eventlog,
            'eventname': eventname,
            'eventstate': eventstate,
            'eventid': event,
            'eventtime': eventtime,
            'interface': INTERFACE,
            'version': remote.extended_version(request.session['token'])['version'],
            'username': username
        }
        html = t.render(RequestContext(request, vars))

        response_obj["message"] = "success.",
        response_obj["collections"] = {"eventlog": html}
        return JsonResponse(response_obj, status = 200)
    else:
        return JsonResponse(response_obj, status = 405)

# ======================================================================

def random_mac(request, virttype="xenpv"):
    """
    Used in an ajax call to fill in a field with a mac address.
    """
    # FIXME: not exposed in UI currently
    if not test_user_authenticated(request):
        return login(request, expired=True)

    if request.method == "GET":
        random_mac = remote.get_random_mac(virttype, request.session['token'])
        return HttpResponse(random_mac)
    else:
        return JsonResponse(gen_response_obj(request), status = 405)

# ======================================================================

# @require_POST
def sync(request):
    """
    Runs 'cobbler sync' from the API when the user presses the sync button.
    """
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/sync", expired=True)

    if request.method == "POST":
        remote.background_sync({"verbose": "True"}, request.session['token'])
        # return HttpResponseRedirect("/sscobbler/task_created")
        return JsonResponse({'status': True, 'message': None, 'url': '/sscobbler/task_created'})
    else:
        return JsonResponse(gen_response_obj(request), status = 405)

# ======================================================================

# @require_POST
def reposync(request):
    """
    Syncs all repos that are configured to be synced.
    """
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/reposync", expired=True)

    if request.method == "POST":
        remote.background_reposync({"names": "", "tries": 3}, request.session['token'])
        # return HttpResponseRedirect("/sscobbler/task_created")
        return JsonResponse({'status': True, 'message': None, 'url': '/sscobbler/task_created'})
    else:
        return JsonResponse(gen_response_obj(request), status = 405)

# ======================================================================

# @require_POST
def hardlink(request):
    """
    Hardlinks files between repos and install trees to save space.
    """
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/hardlink", expired=True)

    if request.method == "POST":
        remote.background_hardlink({}, request.session['token'])
        # return HttpResponseRedirect("/sscobbler/task_created")
        return JsonResponse({'status': True, 'message': None, 'url': '/sscobbler/task_created'})
    else:
        return JsonResponse(gen_response_obj(request), status = 405)

# ======================================================================

# @require_POST
def replicate(request):
    """
    Replicate configuration from the central cobbler server, configured
    in /etc/cobbler/settings (note: this is uni-directional!)

    FIXME: this is disabled because we really need a web page to provide options for
    this command.

    """
    # settings = remote.get_settings()
    # options = settings # just load settings from file until we decide to ask user (later?)
    # remote.background_replicate(options, request.session['token'])
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/replicate", expired=True)

    if request.method == "POST":
        # return HttpResponseRedirect("/sscobbler/task_created")
        return JsonResponse({'status': True, 'message': None, 'url': '/sscobbler/task_created'})
    else:
        return JsonResponse(gen_response_obj(request), status = 405)

# ======================================================================

def __names_from_dicts(lod, optional=True):
    """
    Tiny helper function.
    Get the names out of an array of dictionaries that the remote interface
    returns.
    """
    results = []
    if optional:
        results.append("<<None>>")
    for x in lod:
        results.append(x["name"])
    results.sort()
    return results

# ======================================================================

def generic_edit(request, what=None, obj_name=None, editmode="new"):
    """
    Presents an editor page for any type of object.
    While this is generally standardized, systems are a little bit special.
    """
    target = ""
    if obj_name is not None:
        target = "/%s" % obj_name
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/%s/edit%s" % (what, target), expired=True)

    response_obj = gen_response_obj(request)
    if request.method == "GET":
        obj = None

        child = False
        if what == "subprofile":
            what = "profile"
            child = True

        if obj_name is not None:
            editable = remote.check_access_no_fail(request.session['token'], "modify_%s" % what, obj_name)
            obj = remote.get_item(what, obj_name, False)
        else:
            editable = remote.check_access_no_fail(request.session['token'], "new_%s" % what, None)
            obj = None

        interfaces = {}
        if what == "system":
            if obj:
                interfaces = obj.get("interfaces", {})
            else:
                interfaces = {}

        fields = get_fields(what, child, obj)
        if what == "system":
            fields += get_network_interface_fields()

        # create the autoinstall pulldown list
        autoinstalls = remote.get_autoinstall_templates()
        autoinstall_list = ["", "<<inherit>>"]
        for autoinstall in autoinstalls:
            autoinstall_list.append(autoinstall)

        # populate some select boxes
        if what == "profile":
            if (obj and obj["parent"] not in (None, "")) or child:
                __tweak_field(fields, "parent", "choices", __names_from_dicts(remote.get_profiles()))
            else:
                __tweak_field(fields, "distro", "choices", __names_from_dicts(remote.get_distros()))
            __tweak_field(fields, "autoinstall", "choices", autoinstall_list)
            __tweak_field(fields, "repos", "choices", __names_from_dicts(remote.get_repos()))
            __tweak_field(fields, "mgmt_classes", "choices", __names_from_dicts(remote.get_mgmtclasses(), optional=False))

        elif what == "system":
            __tweak_field(fields, "profile", "choices", __names_from_dicts(remote.get_profiles()))
            __tweak_field(fields, "image", "choices", __names_from_dicts(remote.get_images(), optional=True))
            __tweak_field(fields, "autoinstall", "choices", autoinstall_list)
            __tweak_field(fields, "mgmt_classes", "choices", __names_from_dicts(remote.get_mgmtclasses(), optional=False))

        elif what == "mgmtclass":
            __tweak_field(fields, "packages", "choices", __names_from_dicts(remote.get_packages()))
            __tweak_field(fields, "files", "choices", __names_from_dicts(remote.get_files()))

        elif what == "distro":
            __tweak_field(fields, "arch", "choices", remote.get_valid_archs())
            __tweak_field(fields, "os_version", "choices", remote.get_valid_os_versions())
            __tweak_field(fields, "breed", "choices", remote.get_valid_breeds())
            __tweak_field(fields, "mgmt_classes", "choices", __names_from_dicts(remote.get_mgmtclasses(), optional=False))

        elif what == "image":
            __tweak_field(fields, "arch", "choices", remote.get_valid_archs())
            __tweak_field(fields, "breed", "choices", remote.get_valid_breeds())
            __tweak_field(fields, "os_version", "choices", remote.get_valid_os_versions())
            __tweak_field(fields, "autoinstall", "choices", autoinstall_list)

        # if editing save the fields in the session for comparison later
        if editmode == "edit":
            request.session['%s_%s' % (what, obj_name)] = fields

        # build UI tabs metadata
        if what == "distro":
            sections_data = field_ui_info.DISTRO_UI_FIELDS_MAPPING
        elif what == "file":
            sections_data = field_ui_info.FILE_UI_FIELDS_MAPPING
        elif what == "image":
            sections_data = field_ui_info.IMAGE_UI_FIELDS_MAPPING
        elif what == "mgmtclass":
            sections_data = field_ui_info.MGMTCLASS_UI_FIELDS_MAPPING
        elif what == "package":
            sections_data = field_ui_info.PACKAGE_UI_FIELDS_MAPPING
        elif what == "profile":
            sections_data = field_ui_info.PROFILE_UI_FIELDS_MAPPING
        elif what == "repo":
            sections_data = field_ui_info.REPO_UI_FIELDS_MAPPING
        elif what == "system":
            sections_data = field_ui_info.SYSTEM_UI_FIELDS_MAPPING
        sections = _create_sections_metadata(what, sections_data, fields)
        t = get_template('generic_edit.tmpl')
        inames = interfaces.keys()
        inames.sort()
        html = t.render(RequestContext(request, {
            'what': what,
            'sections': sections,
            'subobject': child,
            'editmode': editmode,
            'editable': editable,
            'interfaces': interfaces,
            'interface_names': inames,
            'interface_length': len(inames),
            'interface': INTERFACE,
            'version': remote.extended_version(request.session['token'])['version'],
            'username': username,
            'name': obj_name,
        }))

        response_obj["message"] = "success.",
        response_obj["collections"] = {"generic_edit": html}
        return JsonResponse(response_obj, status = 200)
    else:
        return JsonResponse(response_obj, status = 405)

# ======================================================================

# @require_POST
def generic_save(request, what):
    """
    Saves an object back using the cobbler API after clearing any 'generic_edit' page.
    """
    if not test_user_authenticated(request):
        return login(request, next="/sscobbler/%s/list" % what, expired=True)

    if request.method == "POST":
        # load request fields and see if they are valid
        editmode = request.POST.get('editmode', 'edit')
        obj_name = request.POST.get('name', "")
        subobject = request.POST.get('subobject', "False")

        if subobject == "False":
            subobject = False
        else:
            subobject = True

        if obj_name == "":
            return error_page(request, "Required field name is missing")

        prev_fields = []
        if "%s_%s" % (what, obj_name) in request.session and editmode == "edit":
            prev_fields = request.session["%s_%s" % (what, obj_name)]

        # grab the remote object handle
        # for edits, fail in the object cannot be found to be edited
        # for new objects, fail if the object already exists
        if editmode == "edit":
            if not remote.has_item(what, obj_name):
                return error_page(request, "Failure trying to access item %s, it may have been deleted." % (obj_name))
            obj_id = remote.get_item_handle(what, obj_name, request.session['token'])
        else:
            if remote.has_item(what, obj_name):
                return error_page(request, "Could not create a new item %s, it already exists." % (obj_name))
            obj_id = remote.new_item(what, request.session['token'])

        # system needs either profile or image to be set
        # fail if both are not set
        if what == "system":
            profile = request.POST.getlist('profile')
            image = request.POST.getlist('image')
            if "<<None>>" in profile and "<<None>>" in image:
                return error_page(request, "Please provide either a valid profile or image for the system")

        # walk through our fields list saving things we know how to save
        fields = get_fields(what, subobject)

        for field in fields:

            if field['name'] == 'name' and editmode == 'edit':
                # do not attempt renames here
                continue
            else:
                # check and see if the value exists in the fields stored in the session
                prev_value = None
                for prev_field in prev_fields:
                    if prev_field['name'] == field['name']:
                        prev_value = prev_field['value']
                        break

                value = request.POST.get(field['name'], None)
                # Checkboxes return the value of the field if checked, otherwise None
                # convert to True/False
                if field["html_element"] == "checkbox":
                    if value == field['name']:
                        value = True
                    else:
                        value = False

                # Multiselect fields are handled differently
                if field["html_element"] == "multiselect":
                    values = request.POST.getlist(field['name'])
                    value = []
                    if '<<inherit>>' in values:
                        value = '<<inherit>>'
                    else:
                        for single_value in values:
                            if single_value != "<<None>>":
                                value.insert(0, single_value)

                if value is not None:
                    if value == "<<None>>":
                        value = ""
                    if value is not None and (not subobject or field['name'] != 'distro') and value != prev_value:
                        try:
                            remote.modify_item(what, obj_id, field['name'], value, request.session['token'])
                        except Exception, e:
                            return error_page(request, str(e))

        # special handling for system interface fields
        # which are the only objects in cobbler that will ever work this way
        if what == "system":
            network_interface_fields = get_network_interface_fields()
            interfaces = request.POST.get('interface_list', "").split(",")
            for interface in interfaces:
                if interface == "":
                    continue
                ifdata = {}
                for field in network_interface_fields:
                    ifdata["%s-%s" % (field["name"], interface)] = request.POST.get("%s-%s" % (field["name"], interface), "")
                ifdata = strip_none(ifdata)
                # FIXME: I think this button is missing.
                present = request.POST.get("present-%s" % interface, "")
                original = request.POST.get("original-%s" % interface, "")
                try:
                    if present == "0" and original == "1":
                        remote.modify_system(obj_id, 'delete_interface', interface, request.session['token'])
                    elif present == "1":
                        remote.modify_system(obj_id, 'modify_interface', ifdata, request.session['token'])
                except Exception, e:
                    return error_page(request, str(e))

        try:
            remote.save_item(what, obj_id, request.session['token'], editmode)
        except Exception, e:
            return error_page(request, str(e))

        # return HttpResponseRedirect('/sscobbler/%s/list' % what)
        url = '/sscobbler/%s/list' % what
        return JsonResponse({'status': True, 'message': None, 'url': url})
    else:
        return JsonResponse(gen_response_obj(request), status = 405)

# ======================================================================
# Login/Logout views

def test_user_authenticated(request):
    global remote
    global username
    global url_cobbler_api

    if url_cobbler_api is None:
        url_cobbler_api = local_get_cobbler_api_url()

    remote = xmlrpclib.Server(url_cobbler_api, allow_none=True)

    # if we have a token, get the associated username from
    # the remote server via XMLRPC. We then compare that to
    # the value stored in the session.  If everything matches up,
    # the user is considered successfully authenticated
    if 'token' in request.session and request.session['token'] != '':
        try:
            if remote.token_check(request.session['token']):
                token_user = remote.get_user_from_token(request.session['token'])
                if 'username' in request.session and request.session['username'] == token_user:
                    username = request.session['username']
                    return True
        except:
            # just let it fall through to the 'return False' below
            pass
    return False

def login(request, next=None, message=None, expired=False):
    global remote
    global url_cobbler_api
    global username

    from sscop_config import COBBLER_USERNAME as username
    from sscop_config import COBBLER_PASSWORD as password

    if expired and not message:
        if INTERFACE_LANG == 'en':
            message = r'Please Contact Administrator for username and password!'
        else:
            message = r"请联系管理员获取用户名与密码！"

    content = {
        'interface': INTERFACE,
        'next': next,
        'message': message
    }

    if url_cobbler_api is None:
        url_cobbler_api = local_get_cobbler_api_url()

    remote = xmlrpclib.Server(url_cobbler_api, allow_none=True)
    token = remote.login(username, password)

    if token:
        request.session['username'] = username
        request.session['token'] = token
        return HttpResponseRedirect(next)
    else:
        return HttpResponseRedirect("/")
