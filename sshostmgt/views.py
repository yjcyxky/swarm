# -*- coding: utf-8 -*-
import logging
from django.http import JsonResponse
from django.utils.http import urlencode
from django.shortcuts import redirect, reverse
from sshostmgt.dracclient.client import DRACClient
from sshostmgt.exceptions import NoSuchHost, NoSuchField
from sshostmgt.models import get_client, ping, get_ipmi_ipaddr, get_hosts
from sshostmgt.utils import gen_dict

logger = logging.getLogger(__name__)

def url_for(base_uri, path, **query_args):
    return u'%s/%s?%s' % (base_uri, path, urlencode(query_args))

def get_ipmi_status(request, hostname = None):
    response_obj = {
        "message": "success",
        "collections": {
            hostname: {
                "ipmi_alive": "yes",
            }
        },
        "api_uri": request.get_raw_uri()
    }
    try:
        ipmi_ipaddr = get_ipmi_ipaddr(hostname)
        if ipmi_ipaddr and ping(ipmi_ipaddr):
            logger.info("%s's IPMI is alive" % hostname)
            response_obj["message"] = "%s's IPMI is alive" % hostname
            return JsonResponse(response_obj, status = 200)
        else:
            logger.info("%s's IPMI is not alive" % hostname)
            response_obj["message"] = "%s's IPMI is alive" % hostname
            response_obj["collections"][hostname]["ipmi_alive"] = "no"
            return JsonResponse(response_obj, status = 404)
    except NoSuchHost as e:
        logger.warning(str(e))
        response_obj["message"] = str(e)
        response_obj["collections"][hostname]["ipmi_alive"] = "Unknown"
        return JsonResponse(response_obj, status = 404)

def get_all_hosts(request):
    response_obj = {
        "message": "Method Not Allowed.",
        "collections": {
        },
        "api_uri": request.get_raw_uri()
    }
    if request.method == "POST":
        return JsonResponse(response_obj, status = 405)
    elif request.method == "GET":
        logger.debug("Request: %s" % dir(request))
        query_args = request.GET
        logger.info("Query Args: %s, %s, %s" % (str(query_args), type(query_args), dir(query_args)))
        filter_keys = ("host_uuid", "hostname", "tag_name")
        filters = gen_dict(filter_keys, query_args)
        keys = ("order_by", "limiting", "which_page")
        hosts = get_hosts(filters, **gen_dict(keys, query_args))
        logger.info("Host list: %s" % str(hosts))
        logger.debug("The type of hosts: %s" % type(hosts))
        if hosts:
            for item in hosts:
                response_obj["collections"][item.get("hostname")] = item
            response_obj["message"] = "success"
            return JsonResponse(response_obj, status = 200)
        else:
            response_obj["message"] = "Can't get any host."
            return JsonResponse(response_obj, status = 404)

def get_host_info(request, hostname = None):
    client = get_client(hostname)
    response_obj = {
        "message": "success",
        "collections": {
            hostname: {
                "status": "ok",
                "power_state": "Unknown",
                "cpus_info": [],
                "memory_info": [],
                "nics_info": [],
                "virtual_disks_info": [],
                "physical_disks_info": []
            }
        },
        "api_uri": request.get_raw_uri()
    }
    host_collection = response_obj["collections"][hostname]
    if client:
        host_collection["power_state"] = client.get_power_state()
        host_collection["cpus_info"] = client.list_cpus()
        host_collection["memory_info"] = client.list_memory()
        host_collection["nics_info"] = client.list_nics()
        host_collection["virtual_disks_info"] = client.list_virtual_disks()
        host_collection["physical_disks_info"] = client.list_physical_disks()
        return JsonResponse(response_obj, status = 200)
    else:
        response_obj["message"] = "Some errors happen, not get any information."
        host_collection["status"] = "warning"
        return JsonResponse(response_obj, status = 404)


def shutdown(request, hostname = None):
    client = get_client(hostname)
    response_obj = {
        "message": "success",
        "collections": {
            hostname: {
                "message": "shutdown success",
                "status": "ok",
                "power_state": "POWER_OFF"
            }
        },
        "api_uri": request.get_raw_uri()
    }
    host_collection = response_obj["collections"][hostname]
    if client:
        power_state = client.get_power_state()
        if power_state == "POWER_ON":
            client.set_power_state("POWER_OFF")
            return JsonResponse(response_obj, status = 202)
        elif power_state == "POWER_OFF":
            return JsonResponse(response_obj, status = 403)
        elif power_state == "REBOOT":
            host_collection["message"] = "reboot state, please retry later."
            host_collection["status"] = "warning"
            host_collection["power_state"] = "REBOOT"
            return JsonResponse(response_obj, status = 403)
    else:
        host_collection["message"] = "No such host."
        host_collection["status"] = "warning"
        host_collection["power_state"] = "Unknown"
        response_obj["message"] = "No such host."
        return JsonResponse(response_obj, status = 404)

def reboot(request, hostname = None):
    client = get_client(hostname)
    response_obj = {
        "message": "success",
        "collections": {
            hostname: {
                "message": "Reboot success",
                "status": "ok",
                "power_state": "REBOOT"
            }
        },
        "api_uri": request.get_raw_uri()
    }
    host_collection = response_obj["collections"][hostname]
    if client:
        power_state = client.get_power_state()
        if power_state == "POWER_ON":
            client.set_power_state("REBOOT")
            return JsonResponse(response_obj, status = 202)
        elif power_state == "POWER_OFF":
            return redirect('wakeup', hostname = hostname)
        elif power_state == "REBOOT":
            host_collection["message"] = "reboot state, please retry later."
            host_collection["status"] = "warning"
            return JsonResponse(response_obj, status = 403)
    else:
        host_collection["message"] = "No such host."
        host_collection["status"] = "warning"
        host_collection["power_state"] = "Unknown"
        response_obj["message"] = "No such host."
        return JsonResponse(response_obj, status = 404)

def wakeup(request, hostname = None):
    client = get_client(hostname)
    response_obj = {
        "message": "success",
        "collections": {
            hostname: {
                "message": "Wake up success",
                "status": "ok",
                "power_state": "POWER_ON"
            }
        },
        "api_uri": request.get_raw_uri()
    }
    host_collection = response_obj["collections"][hostname]
    if client:
        power_state = client.get_power_state()
        if power_state == "POWER_ON":
            host_collection["message"] = "Power on, no any process."
            host_collection["status"] = "warning"
            return JsonResponse(response_obj, status = 403)
        elif power_state == "POWER_OFF":
            client.set_power_state("POWER_ON")
            host_collection["message"] = "Wake up success"
            return JsonResponse(response_obj, status = 202)
        elif power_state == "REBOOT":
            host_collection["message"] = "reboot state, please retry later."
            host_collection["power_state"] = "REBOOT"
            host_collection["status"] = "warning"
            return JsonResponse(response_obj, status = 403)
    else:
        host_collection["message"] = "No such host."
        host_collection["status"] = "warning"
        host_collection["power_state"] = "Unknown"
        response_obj["message"] = "No such host."
        return JsonResponse(response_obj, status = 404)

def get_power_status(request, hostname = None):
    """Get the power status of the specified host

    :param request: http request
    :param hostname: hostname of user specified host
    :returns: JSON file, show the power state and request status.

    TODO: 增加更多dracclient初始化参数
    """
    client = get_client(hostname)
    response_obj = {
        "message": "success",
        "collections": {
            hostname: {
                "message": "",
                "status": "ok",
                "power_state": ""
            }
        },
        "api_uri": request.get_raw_uri()
    }
    host_collection = response_obj["collections"][hostname]
    if client:
        power_state = client.get_power_state()
        if power_state:
            host_collection["message"] = "Power state: %s" % power_state.lower()
            host_collection["power_state"] = power_state
            return JsonResponse(response_obj, status = 200)
        else:
            host_collection["message"] = "Can't get the power status"
            host_collection["status"] = "error"
            host_collection["power_state"] = "Unknown"
            return JsonResponse(response_obj, status = 404)
    else:
        host_collection["message"] = "No such host."
        host_collection["status"] = "warning"
        host_collection["power_state"] = "Unknown"
        response_obj["message"] = "No such host."
        return JsonResponse(response_obj, status = 404)

def add_host(request):
    """Add a host record

    :param request: http request
    :returns: JSON file, show the created host record.
    """
    response_obj = {
        "message": "Method Not Allowed.",
        "collections": {
        },
        "api_uri": request.get_raw_uri()
    }
    if request.method == "GET":
        return JsonResponse(response_obj, status = 405)
    elif request.method == "POST":
        request_args = request.POST
        host_uuid = request_args.get("host_uuid", None)
        hostname = request_args.get("hostname", None)
        host_info_keys = ("ipmi_mac", "ipmi_addr", "ipmi_username", "ipmi_passwd"
                          "power_state", "host_uuid", "hostname")
        host_info = gen_dict(host_info_keys, request_args)
        try:
            if host_uuid and hostname:
                set_host(**host_info)
                response_obj["message"] = "Host created."
                # TODO: Add host information
                return JsonResponse(response_obj, status = 201)
                # May be you want to redirect to "get_host_info" directly
                # return redirect("get_host_info", hostname = hostname)
            else:
                raise NoSuchField("You must specify a host_uuid.")
        except NoSuchField as e:
            logger.error(str(e))
            response_obj["message"] = str(e)
            return JsonResponse(response_obj, status = 400)
