# -*- coding: utf-8 -*-
from django.http import JsonResponse
from sshostmgt.dracclient.client import DRACClient

def get_client(hostname, **kwargs):
    username = get_username(hostname)
    passwd = get_passwd(hostname, username)
    client = DRACClient(hostname, username, passwd, **kwargs)
    return client

def get_username(hostname):
    '''
    功能：从数据库获取主机IPMI账户
    '''
    username = 'root'
    return username

def get_passwd(hostname, username):
    '''
    功能：从数据库中获取IPMI账户密码
    '''
    passwd = 'calvin'
    return passwd

def get_req_info(request, *args):
    '''
    功能：从request中获取指定字段的值
    输入：request
         请求字段字符串，有多个时依次输入
    返回值：输出为list，排列顺序依据传入参数的顺序; 未找到值时，返回None；
    '''
    result_list = []
    for arg in args:
        result_list.append(request.session.get(arg))
    return result_list

def get_host_info(request, hostname=None):
    pass

def shutdown(request, hostname=None):
    pass

def reboot(request, hostname=None):
    pass

def wakeup(request, hostname=None):
    pass

def get_power_status(request, hostname=None):
    '''
    功能：
    TODO: 增加更多DRACClient初始化参数
    '''
    if hostname:
        client = get_client(hostname)
        power_state = client.get_power_state()
        if power_state:
            return JsonResponse({'state': 'ok', 'message': None, 'power_state': power_state, 'hostname': hostname})
        else:
            return JsonResponse({'state': 'error', 'message': 'Can\'t get the power status', 'power_state': 'Unknown', 'hostname': hostname})

def set_ipmi_info(request, hostname=None):
    '''
    功能：设置指定主机的IPMI信息，包括开机启动顺序、账号、密码等
    '''
    if hostname:
        client = get_client(hostname)

def get_ipmi_info(request, hostname=None):
    '''
    功能：获取指定主机的IPMI信息
    '''
    pass
