# -*- coding: utf-8 -*-
from django.http import JsonResponse
from django.shortcuts import render
from sshostmgt.dracclient.client import DRACClient
from sshostmgt.exceptions import NoSuchHost
from sshostmgt.models import get_ipmi_ipaddr, get_username, get_passwd, get_client

def redirect_to_hosts():
    return redirect('get_all_hosts')

def get_all_hosts():
    pass

def get_req_info(request, *args):
    """
    功能：从request中获取指定字段的值
    输入：request
         请求字段字符串，有多个时依次输入
    返回值：输出为list，排列顺序依据传入参数的顺序; 未找到值时，返回None；
    """
    result_list = []
    for arg in args:
        result_list.append(request.session.get(arg))
    return result_list

def get_host_info(request, hostname=None):
    pass

def shutdown(request, hostname=None):
    client = get_client(hostname)
    if client:
        power_state = client.get_power_state()
        if power_state == "POWER_ON":
            client.set_power_state("POWER_OFF")
            return JsonResponse({
                "status": "ok", 
                "message": "shutdown success", 
                "power_state": "POWER_OFF", 
                "hostname": hostname
            })
        elif power_state == "POWER_OFF":
            return JsonResponse({
                "status": "ok", 
                "message": "shutdown success", 
                "power_state": "POWER_OFF", 
                "hostname": hostname
            })
        elif power_state == "REBOOT":
            return JsonResponse({
                "status": "warning",
                "message": "reboot state, please retry later.",
                "power_state": "REBOOT",
                "hostname": hostname
            })
    else:
        return JsonResponse({
            "status": "warning",
            "message": "No such host.",
            "power_state": "Unknown",
            "hostname": hostname
        })

def reboot(request, hostname=None):
    client = get_client(hostname)
    if client:
        power_state = client.get_power_state()
        if power_state == "POWER_ON":
            client.set_power_state("REBOOT")
            return JsonResponse({
                "status": "ok", 
                "message": "Reboot success", 
                "power_state": "REBOOT", 
                "hostname": hostname
            })
        elif power_state == "POWER_OFF":
            return redirect('wakeup', hostname = hostname)
        elif power_state == "REBOOT":
            return JsonResponse({
                "status": "warning",
                "message": "reboot state, please retry later.",
                "power_state": "REBOOT",
                "hostname": hostname
            })
    else:
        return JsonResponse({
            "status": "warning",
            "message": "No such host.",
            "power_state": "Unknown",
            "hostname": hostname
        })

def wakeup(request, hostname=None):
    client = get_client(hostname)
    if client:
        power_state = client.get_power_state()
        if power_state == "POWER_ON":
            return JsonResponse({
                "status": "warning", 
                "message": "Power on, no any process", 
                "power_state": "POWER_ON", 
                "hostname": hostname
            })
        elif power_state == "POWER_OFF":
            client.set_power_state("POWER_ON")
            return JsonResponse({
                "status": "ok",
                "message": "Wake up success",
                "power_state": "POWER_ON",
                "hostname": hostname
            })
        elif power_state == "REBOOT":
            return JsonResponse({
                "status": "warning",
                "message": "reboot state, please retry later.",
                "power_state": "REBOOT",
                "hostname": hostname
            })
    else:
        return JsonResponse({
            "status": "warning",
            "message": "No such host.",
            "power_state": "Unknown",
            "hostname": hostname
        })

def get_power_status(request, hostname=None):
    """Get the power status of the specified host
    
    :param request: http request
    :param hostname: hostname of user specified host
    :returns: JSON file, show the power state and request status.
    
    TODO: 增加更多dracclient初始化参数
    """
    client = get_client(hostname)
    if client:
        power_state = client.get_power_state()
        if power_state:
            return JsonResponse({
                "status": "ok", 
                "message": "Power state: %s" % power_state.lower(), 
                "power_state": power_state, 
                "hostname": hostname
            })
        else:
            return JsonResponse({
                "status": "error", 
                "message": "Can't get the power status", 
                "power_state": "Unknown", 
                "hostname": hostname
            })
    else:
        return JsonResponse({
            "status": "warnings", 
            "message": "No such host", 
            "power_state": "Unknown", 
            "hostname": hostname
        })

def set_ipmi_info(request, hostname=None):
    """
    功能：设置指定主机的IPMI信息，包括开机启动顺序、账号、密码等
    """
    client = get_client(hostname)

def get_ipmi_info(request, hostname=None):
    """
    功能：获取指定主机的IPMI信息
    """
    pass
