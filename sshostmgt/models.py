# -*- coding: utf-8 -*-
import logging, copy
from datetime import datetime
from django.db import models
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
# from sshostmgt.exceptions import NoSuchField, FormatError
from utils import gen_dict, isNone, merge_dicts, allNone

logger = logging.getLogger(__name__)

class IPMI(models.Model):
    POWER_STATE = (
        ('power_on', 'POWER_ON'),
        ('power_off', 'POWER_OFF'),
        ('reboot', 'REBOOT'),
        ('unknown', 'UNKNOWN'),
        ('changed', 'CHANGED'),
        ('POWER_ON', 'POWER_ON'),
        ('POWER_OFF', 'POWER_OFF'),
        ('REBOOT', 'REBOOT'),
        ('UNKNOWN', 'UNKNOWN'),
        ('CHANGED', 'CHANGED')
    )
    ipmi_uuid = models.CharField(max_length = 128, primary_key = True)
    ipmi_mac = models.CharField(max_length = 17, unique = True)
    ipmi_addr = models.CharField(max_length = 15, unique = True)
    ipmi_username = models.CharField(max_length = 32, default = 'root')
    ipmi_passwd = models.CharField(max_length = 32, default = 'calvin')
    power_state = models.CharField(max_length = 10, choices = POWER_STATE, default = 'POWER_OFF')
    last_update_time = models.DateTimeField()
    first_add_time = models.DateTimeField()

    def __str__(self):
        return self.ipmi_uuid

    class Meta:
        ordering = ('ipmi_addr',)

class BIOS(models.Model):
    bios_uuid = models.CharField(max_length = 128, primary_key = True)

class RAID(models.Model):
    raid_uuid = models.CharField(max_length = 128, primary_key = True)

class System(models.Model):
    system_uuid = models.CharField(max_length = 128, primary_key = True)

class Tag(models.Model):
    tag_uuid = models.CharField(max_length = 128, primary_key = True)
    tag_name_alias = models.CharField(max_length = 32, null = True)
    tag_name = models.CharField(max_length = 32, unique = True)
    # label by choosed color
    label_color = models.CharField(max_length = 32, default = '#23d7bc')
    common_used = models.BooleanField()

    def __str__(self):
        return self.tag_uuid

    class Meta:
        ordering = ('tag_name',)

class Host(models.Model):
    host_uuid = models.CharField(max_length = 128, primary_key = True)
    hostname = models.CharField(max_length = 64, unique = True)
    mgmt_ip_addr = models.CharField(max_length = 16, unique = True)
    ipmi = models.OneToOneField(IPMI, on_delete = models.CASCADE)
    tags = models.ManyToManyField(Tag)
    # bios = models.OneToOneField(BIOS, on_delete = models.CASCADE)
    # system = models.OneToOneField(System, on_delete = models.CASCADE)

    def __str__(self):
        return "%s-%s" % (self.host_uuid, self.hostname)

    class Meta:
        ordering = ('hostname',)

class CPU(models.Model):
    cpu_uuid = models.CharField(max_length = 128, primary_key = True)
    host = models.ForeignKey(Host, on_delete = models.CASCADE)

class Network(models.Model):
    network_uuid = models.CharField(max_length = 128, primary_key = True)
    host = models.ForeignKey(Host, on_delete = models.CASCADE)

class Storage(models.Model):
    storage_uuid = models.CharField(max_length = 128, primary_key = True)
    host = models.ForeignKey(Host, on_delete = models.CASCADE)

class Memory(models.Model):
    memory_uuid = models.CharField(max_length = 128, primary_key = True)
    host = models.ForeignKey(Host, on_delete = models.CASCADE)
