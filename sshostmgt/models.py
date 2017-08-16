# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from django.db import models
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from sshostmgt.dracclient.client import DRACClient
from sshostmgt.exceptions import NoSuchField

logger = logging.getLogger(__name__)

class IPMI(models.Model):
    POWER_STATE = (
        ('power_on', 'POWER_ON'),
        ('power_off', 'POWER_OFF'),
        ('reboot', 'REBOOT'),
        ("unknown", 'UNKNOWN')
    )
    ipmi_mac = models.CharField(max_length = 17, primary_key = True)
    ipmi_addr = models.CharField(max_length = 15, unique = True)
    ipmi_username = models.CharField(max_length = 32, default = 'root')
    ipmi_passwd = models.CharField(max_length = 32, default = 'calvin')
    power_state = models.CharField(max_length = 10, choices = POWER_STATE)
    last_update_time = models.DateTimeField()
    first_add_time = models.DateTimeField()

class BIOS(models.Model):
    pass

class System(models.Model):
    pass

class Host(models.Model):
    host_uuid = models.CharField(max_length = 32, primary_key = True)
    hostname = models.CharField(max_length = 64, unique = True)
    ipmi = models.OneToOneField(IPMI, on_delete = models.CASCADE)
    bios = models.OneToOneField(BIOS, on_delete = models.CASCADE)
    system = models.OneToOneField(System, on_delete = models.CASCADE)

class Tag(models.Model):
    tag_name = models.CharField(max_length = 32)
    members = models.ManyToManyField(Host, through = "Membership")

    def __str__(self):
        return self.tag_name

class Membership(models.Model):
    host = models.ForeignKey(Host, on_delete = models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete = models.CASCADE)

class CPU(models.Model):
    host = models.ForeignKey(Host, on_delete = models.CASCADE)

class Network(models.Model):
    host = models.ForeignKey(Host, on_delete = models.CASCADE)

class Storage(models.Model):
    host = models.ForeignKey(Host, on_delete = models.CASCADE)

class Memory(models.Model):
    host = models.ForeignKey(Host, on_delete = models.CASCADE)

def get_client(hostname, **kwargs):
    """Get a client instance
    """
    ipmi_info = get_ipmi_info(hostname)
    logger.info("IPMI Information: %s" % str(ipmi_info))
    username = ipmi_info.get("username")
    passwd = ipmi_info.get("passwd")
    ip_addr = ipmi_info.get("ip_addr")
    if username and passwd and ip_addr:
        client = DRACClient(ip_addr, username, passwd, **kwargs)
        return client
    else:
        return None

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
    first_pos = nums - (nums / limiting - which_page + 1) * limiting
    second_pos = nums - (nums / limiting - which_page) * limiting
    return queryset[first_pos, second_pos]

def get_hosts(filters = None, order_by = None, limiting = None, which_page = None):
    """Get information of hosts.
    1. You can filter results by using filter parameter.
    2. Order results by using order_by parameter.
    3. Page break by using limiting, which_page and total numbers of results.
    :param filters(Dict): A string sets for filtering results(exact matching).
    :param order_by(String): A string for ordering results, it must be a filed of Host class.
    :param limiting(Integer): A integer for specify numbers of items in one page.
    :param which_page(Integer): A integer for specify which page you want to
    :returns: return a queryset that contains hosts you queried
    """
    order_items = ["host_uuid", "hostname"]
    filter_items = ["host_uuid", "hostname"]
    hosts = Host.objects.all()
    new_hosts = hosts
    new_filters = {}
    # filter
    if isinstance(filters, dict):
        for key, value in filters:
            if key in filter_items:
                new_filters["%s_exact" % key] = value

        for new_key, new_value in new_filters:
            new_hosts = new_hosts.filter(**{new_key: new_value})

    # page break
    if isinstance(limiting, int) and isinstance(which_page, int):
        new_hosts = get_results_by_page(new_hosts, limiting, which_page)

    # order results
    if isinstance(order_by, str) and order_by in order_items:
        new_hosts = new_hosts.order_by(order_by.lower())

    return new_hosts.values()

def get_host_uuid(hostname):
    try:
        host = Host.objects.get(hostname = hostname)
        logger.info("Query host: %s" % hostname)
        return host.host_uuid if host else None
    except ObjectDoesNotExist as e:
        logger.error(str(e))
        return {}

def get_username(hostname):
    """
    功能：从数据库获取主机IPMI账户
    """
    default_username = "root"
    try:
        host = Host.objects.get(hostname = hostname)
        ipmi_info = host.ipmi
        if ipmi_info:
            return ipmi_info.get("ipmi_username")
        else:
            return default_username
    except ObjectDoesNotExist as e:
        logger.error(str(e))
        return {}

def get_passwd(hostname, username):
    """
    功能：从数据库中获取IPMI账户密码
    """
    default_passwd = "calvin"
    try:
        host = Host.objects.get(hostname = hostname)
        ipmi_info = host.ipmi
        if ipmi_info and ipmi_info.get("ipmi_username") == username:
            return ipmi_info.get("ipmi_passwd")
        else:
            return default_passwd
    except ObjectDoesNotExist as e:
        logger.error(str(e))
        return {}

def get_ipmi_ipaddr(hostname):
    try:
        host = Host.objects.get(hostname = hostname)
        ipmi_info = host.ipmi
        if ipmi_info:
            return ipmi_info.get("ipmi_addr")
        else:
            return None
    except ObjectDoesNotExist as e:
        logger.error(str(e))
        return None

def get_ipmi_info(hostname):
    try:
        host = Host.objects.get(hostname = hostname)
        ipmi_info = host.ipmi
        if ipmi_info:
            return ipmi_info
        else:
            return {}
    except ObjectDoesNotExist as e:
        logger.error(str(e))
        return {}

def update_ipmi_info(hostname):
    client = get_client(hostname)
    if client:
        power_state = client.get_power_state()
        ipmi_info = get_ipmi_info(hostname)
        ipmi_mac = ipmi_info.get("ipmi_mac")
        ipmi = IPMI.objects.get(ipmi_mac = ipmi_mac)
        ipmi.power_state = power_state
        ipmi.last_update_time = datatime.now()
        ipmi.save()
    else:
        raise NoSuchHost("Can't connect to %s by using dracclient" % hostname)

def ping(ipaddress = None):
    import subprocess
    import shlex

    cmd = "ping -c 1 %s" % ipaddress
    args = shlex.split(cmd)

    try:
        subprocess.check_call(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info("Ping IPMI NIC: %s" % ipaddress)
        return True
    except subprocess.CalledProcessError as e:
        logger.warning("Ping IPMI NIC %s: %s" % (ipaddress, str(e)))
        return False

def set_host(**kwargs):
    """Create a host record
    """
    required_args = ["ipmi_mac", "ipmi_addr", "ipmi_username", "ipmi_passwd"
                     "power_state", "host_uuid", "hostname"]

    def check_powerstate(value):
        state_choices = ["power_on", "power_off", "unknown", "reboot"]
        if value is not None and value.lower() in state_choices:
            return value.lower()
        else:
            return "unknown"

    if kwargs is None:
        raise NoSuchField("You must pass information about a host.")
    else:
        last_update_time = first_add_time = datatime.now()
        for item in required_args:
            if item in kwargs.keys():
                pass
            else:
                raise NoSuchField("You must specify the %s value." % item)
        ipmi_info = {
            "ipmi_mac": kwargs.get("ipmi_mac"),
            "ipmi_addr": kwargs.get("ipmi_addr"),
            "ipmi_username": kwargs.get("ipmi_username") or "root",
            "ipmi_passwd": kwargs.get("ipmi_passwd") or "calvin",
            "power_state": check_powerstate(kwargs.get("power_state")),
            "last_update_time": last_update_time,
            "first_add_time": first_add_time,
        }
        ipmi = IPMI.objects.create(**ipmi_info)

        host_info = {
            "host_uuid": kwargs.get("host_uuid"),
            "hostname": kwargs.get("hostname"),
            "ipmi": ipmi,
            "bios": None,
            "system": None
        }
        host = Host.objects.create(**host_info)
        host.save()
        logger.info("Save %s to ipmi table." % str(ipmi))
        logger.info("Save (%s) to host table." % str(host_info))
