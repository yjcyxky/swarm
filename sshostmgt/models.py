# -*- coding: utf-8 -*-
from sshostmgt.dracclient.client import DRACClient

from django.apps import apps

def get_client(hostname, **kwargs):
    try:
        username = get_username(hostname)
        passwd = get_passwd(hostname, username)
        ip_addr = get_ipmi_ipaddr(hostname)
        client = DRACClient(ip_addr, username, passwd, **kwargs)
        return client
    except NoSuchHost as e:
        return None

def get_username(hostname):
    """
    功能：从数据库获取主机IPMI账户
    """
    username = "root"
    return username

def get_passwd(hostname, username):
    """
    功能：从数据库中获取IPMI账户密码
    """
    passwd = "calvin"
    return passwd

def get_ipmi_ipaddr(hostname):
    if True:
        return "192.168.1.121"
    else:
        raise NoSuchHost("%s: No such host" % hostname)