# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import logging
from django.db import models

logger = logging.getLogger(__name__)


class Instances(models.Model):
    instance_id = models.AutoField(primary_key=True)
    instance_name = models.CharField(max_length=64, default='default')
    instance_description = models.CharField(max_length=128, default='')

    class Meta:
        db_table = "nagios_instances"


class Objects(models.Model):
    object_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    objecttype_id = models.SmallIntegerField(default='0')
    name1 = models.CharField(max_length=128, default='')
    name2 = models.CharField(max_length=128, null=True, default='')
    is_active = models.SmallIntegerField(default='0')

    class Meta:
        db_table = "nagios_objects"


class Acknowledgements(models.Model):
    acknowledgement_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    entry_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    entry_time_usec = models.IntegerField(default='0')
    acknowledgement_type = models.SmallIntegerField(default='0')
    object_id = models.IntegerField(default='0')
    state = models.SmallIntegerField(default='0')
    author_name = models.CharField(max_length=64, default='')
    comment_data = models.CharField(max_length=255, default='')
    is_sticky = models.SmallIntegerField(default='0')
    persistent_comment = models.SmallIntegerField(default='0')
    notify_contacts = models.SmallIntegerField(default='0')

    class Meta:
        db_table = "nagios_acknowledgements"


class Commands(models.Model):
    command_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    config_type = models.SmallIntegerField(default='0')
    object_id = models.IntegerField(default='0')
    command_line = models.CharField(max_length=255, default='')

    class Meta:
        db_table = "nagios_commands"


class CommentHistory(models.Model):
    commenthistory_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    entry_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    entry_time_usec = models.IntegerField(default='0')
    comment_type = models.SmallIntegerField(default='0')
    entry_type = models.SmallIntegerField(default='0')
    object_id = models.IntegerField(default='0')
    comment_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    internal_comment_id = models.IntegerField(default='0')
    author_name = models.CharField(max_length=64, default='')
    comment_data = models.CharField(max_length=255, default='')
    is_persistent = models.SmallIntegerField(default='0')
    comment_source = models.SmallIntegerField(default='0')
    expires = models.SmallIntegerField(default='0')
    expiration_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    deletion_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    deletion_time_usec = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_commenthistory"


class Comments(models.Model):
    comment_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    entry_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    entry_time_usec = models.IntegerField(default='0')
    commnet_type = models.SmallIntegerField(default='0')
    entry_type = models.SmallIntegerField(default='0')
    object_id = models.IntegerField(default='0')
    comment_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    internal_comment_id = models.IntegerField(default='0')
    author_name = models.CharField(max_length=64, default='')
    comment_data = models.CharField(max_length=255, default='')
    is_persistent = models.SmallIntegerField(default='0')
    comment_source = models.SmallIntegerField(default='0')
    expires = models.SmallIntegerField(default='0')
    expiration_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)

    class Meta:
        db_table = "nagios_comments"


class ConfigFiles(models.Model):
    configfile_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    configfile_type = models.SmallIntegerField(default='0')
    configfile_path = models.CharField(max_length=255, default='')

    class Meta:
        db_table = "nagios_configfiles"


class ConfigFileVariables(models.Model):
    configfilevariable_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    configfile_id = models.IntegerField(default='0')
    varname = models.CharField(max_length=64, default='')
    varvalue = models.CharField(max_length=255, default='')

    class Meta:
        db_table = "nagios_configfilevariables"


class ConnInfo(models.Model):
    conninfo_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    agent_name = models.CharField(max_length=32, default='')
    agent_version = models.CharField(max_length=8, default='')
    disposition = models.CharField(max_length=16, default='')
    connect_source = models.CharField(max_length=16, default='')
    connect_type = models.CharField(max_length=16, default='')
    connect_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    disconnect_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    last_checkin_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    data_start_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    data_end_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    bytes_processed = models.IntegerField(default='0')
    lines_processed = models.IntegerField(default='0')
    entries_processed = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_conninfo"


class Contacts(models.Model):
    contact_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    config_type = models.SmallIntegerField(default='0')
    contact_object_id = models.IntegerField(default='0')
    alias = models.CharField(max_length=64, default='')
    email_address = models.CharField(max_length=64, default='')
    pager_address = models.CharField(max_length=64, default='')
    minimum_importance = models.IntegerField(default='0')
    host_timeperiod_object_id = models.IntegerField(default='0')
    service_timeperiod_object_id = models.IntegerField(default='0')
    host_notifications_enabled = models.SmallIntegerField(default='0')
    service_notifications_enabled = models.SmallIntegerField(default='0')
    can_submit_commands = models.SmallIntegerField(default='0')
    notify_service_recovery = models.SmallIntegerField(default='0')
    notify_service_warning = models.SmallIntegerField(default='0')
    notify_service_unknown = models.SmallIntegerField(default='0')
    notify_service_critical = models.SmallIntegerField(default='0')
    notify_service_flapping = models.SmallIntegerField(default='0')
    notify_service_downtime = models.SmallIntegerField(default='0')
    notify_host_recovery = models.SmallIntegerField(default='0')
    notify_host_down = models.SmallIntegerField(default='0')
    notify_host_unreachable = models.SmallIntegerField(default='0')
    notify_host_flapping = models.SmallIntegerField(default='0')
    notify_host_downtime = models.SmallIntegerField(default='0')

    class Meta:
        db_table = "nagios_contacts"


class ContactAddresses(models.Model):
    contact_address_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    contact_id = models.IntegerField(default='0')
    address_number = models.SmallIntegerField(default='0')
    address = models.CharField(max_length=255, default='')

    class Meta:
        db_table = "nagios_contact_addresses"


class ContactNotificationCommands(models.Model):
    contact_notificationcommand_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    contact_id = models.IntegerField(default='0')
    notification_type = models.SmallIntegerField(default='0')
    command_object_id = models.IntegerField(default='0')
    command_args = models.CharField(max_length=255, default='')

    class Meta:
        db_table = "nagios_contact_notificationcommands"


class ContactGroups(models.Model):
    contactgroup_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    config_type = models.SmallIntegerField(default='0')
    contactgroup_object_id = models.IntegerField(default='0')
    alias = models.CharField(max_length=255, default='')

    class Meta:
        db_table = "nagios_contactgroups"


class ContactGroupMembers(models.Model):
    contactgroup_member_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    contactgroup_id = models.IntegerField(default='0')
    contact_object_id = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_contactgroup_members"


class Notifications(models.Model):
    """
    Description:
    This table is used to store a historical record of host and service
    notifications that have been sent out. For each notification,
    one or more contacts receive notification messages.
    These contact notifications are stored in the contactnotifications table.

    Values:
        notification_type:
            0 = Host notification
            1 = Service notification
        notification_reason:
            0 = Normal notification
            1 = Problem acknowledgement
            2 = Flapping started
            3 = Flapping stopped
            4 = Flapping was disabled
            5 = Downtime started
            6 = Downtime ended
            7 = Downtime was cancelled
            99 = Custom notification
        For Host Notifications:
            0 = UP
            1 = DOWN
            2 = CRITICAL
        For Service Notifications:
            0 = OK
            1 = WARNING
            2 = CRITICAL
            3 = UNKNOWN
        escalated:
            0 = NOT escalated
            1 = Escalated
    Relationships:
        instance_id <--> instances.instance_id
        object_id <--> objects.object_id
    """
    notification_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    notification_type = models.SmallIntegerField(default='0')
    notification_reason = models.SmallIntegerField(default='0')
    object_id = models.IntegerField(default='0')
    start_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    start_time_usec = models.IntegerField(default='0')
    end_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    end_time_usec = models.IntegerField(default='0')
    state = models.SmallIntegerField(default='0')
    output = models.CharField(max_length=255, default='')
    long_output = models.TextField(default='')
    escalated = models.SmallIntegerField(default='0')
    contacts_notified = models.SmallIntegerField(default='0')
    # New Custom Field
    checked = models.BooleanField(default=False)
    checked_time = models.DateTimeField(null=True, default='0000-00-00 00:00:00')

    class Meta:
        db_table = "nagios_notifications"


class ContactNotifications(models.Model):
    contactnotification_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    notification_id = models.IntegerField(default='0')
    contact_object_id = models.IntegerField(default='0')
    start_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    start_time_usec = models.IntegerField(default='0')
    end_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    end_time_usec = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_contactnotifications"


class ContactNotificationMethods(models.Model):
    contactnotificationmethod_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    contactnotification_id = models.IntegerField(default='0')
    start_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    start_time_usec = models.IntegerField(default='0')
    end_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    end_time_usec = models.IntegerField(default='0')
    command_object_id = models.IntegerField(default='0')
    command_args = models.CharField(max_length=255, default='')

    class Meta:
        db_table = "nagios_contactnotificationmethods"


class ContactStatus(models.Model):
    contactstatus_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    contact_object_id = models.IntegerField(default='0')
    status_update_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    host_notifications_enabled = models.SmallIntegerField(default='0')
    service_notifications_enabled = models.SmallIntegerField(default='0')
    last_host_notification = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    last_service_notification = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    modified_attributes = models.IntegerField(default='0')
    modified_host_attributes = models.IntegerField(default='0')
    modified_service_attributes = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_contactstatus"


class CustomVariables(models.Model):
    customvariable_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    object_id = models.IntegerField(default='0')
    config_type = models.SmallIntegerField(default='0')
    has_been_modified = models.SmallIntegerField(default='0')
    varname = models.CharField(max_length=255, default='')
    varvalue = models.CharField(max_length=255, default='')

    class Meta:
        db_table = "nagios_customvariables"


class CustomVariableStatus(models.Model):
    customvariablestatus = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    object_id = models.IntegerField(default='0')
    status_update_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    has_been_modified = models.IntegerField(default='0')
    varname = models.CharField(max_length=255, default='')
    varvalue = models.CharField(max_length=255, default='')

    class Meta:
        db_table = "nagios_customvariablestatus"


class Dbversion(models.Model):
    name = models.CharField(max_length=10, default='')
    version = models.CharField(max_length=10, default='')

    class Meta:
        db_table = "nagios_dbversion"


class DowntimeHistory(models.Model):
    downtimehistory_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    downtime_type = models.SmallIntegerField(default='0')
    object_id = models.IntegerField(default='0')
    entry_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    author_name = models.CharField(max_length=64, default='')
    comment_data = models.CharField(max_length=255, default='')
    internal_downtime_id = models.IntegerField(default='0')
    triggered_by_id = models.IntegerField(default='0')
    is_fixed = models.SmallIntegerField(default='0')
    duration = models.SmallIntegerField(default='0')
    scheduled_start_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    scheduled_end_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    was_started = models.SmallIntegerField(default='0')
    actual_start_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    actual_start_time_usec = models.IntegerField(default='0')
    actual_end_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    actual_end_time_usec = models.IntegerField(default='0')
    was_cancelled = models.SmallIntegerField(default='0')

    class Meta:
        db_table = "nagios_downtimehistory"


class EventHandlers(models.Model):
    eventhandler_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    eventhandler_type = models.SmallIntegerField(default='0')
    object_id = models.IntegerField(default='0')
    state = models.SmallIntegerField(default='0')
    state_type = models.SmallIntegerField(default='0')
    start_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    start_time_usec = models.IntegerField(default='0')
    end_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    end_time_usec = models.IntegerField(default='0')
    command_object_id = models.IntegerField(default='0')
    command_args = models.CharField(max_length=255, default='')
    command_line = models.CharField(max_length=255, default='')
    timeout = models.SmallIntegerField(default='0')
    early_timeout = models.SmallIntegerField(default='0')
    execution_time = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    return_code = models.SmallIntegerField(default='0')
    output = models.CharField(max_length=255, default='')
    long_output = models.TextField(default='')

    class Meta:
        db_table = "nagios_eventhandlers"


class ExternalCommands(models.Model):
    externalcommand_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    entry_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    command_type = models.SmallIntegerField(default='0')
    command_name = models.CharField(max_length=128, default='')
    command_args = models.CharField(max_length=255, default='')

    class Meta:
        db_table = "nagios_externalcommands"


class FlappingHistory(models.Model):
    flappinghistory_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    event_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    event_time_usec = models.IntegerField(default='0')
    event_type = models.SmallIntegerField(default='0')
    reason_type = models.SmallIntegerField(default='0')
    flapping_type = models.SmallIntegerField(default='0')
    object_id = models.IntegerField(default='0')
    percent_state_change = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    low_threshold = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    high_threshold = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    comment_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    internal_comment_id = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_flappinghistory"


class Hosts(models.Model):
    host_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    config_type = models.IntegerField(default='0')
    host_object_id = models.IntegerField(default='0')
    alias = models.CharField(max_length=64, default='')
    display_name = models.CharField(max_length=64, default='')
    address = models.CharField(max_length=128)
    importance = models.IntegerField(default='0')
    check_command_object_id = models.IntegerField(default='0')
    check_command_args = models.CharField(max_length=255, default='')
    eventhandler_command_object_id = models.IntegerField(default='0')
    eventhandler_command_args = models.CharField(max_length=255, default='')
    notification_timeperiod_object_id = models.IntegerField(default='0')
    check_timeperiod_object_id = models.IntegerField(default='0')
    failure_prediction_options = models.CharField(max_length=64, default='')
    check_interval = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    retry_interval = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    max_check_attempts = models.SmallIntegerField(default='0')
    first_notification_delay = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    notification_interval = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    notify_on_down = models.SmallIntegerField(default='0')
    notify_on_unreachable = models.SmallIntegerField(default='0')
    notify_on_recovery = models.SmallIntegerField(default='0')
    notify_on_flapping = models.SmallIntegerField(default='0')
    notify_on_downtime = models.SmallIntegerField(default='0')
    stalk_on_up = models.SmallIntegerField(default='0')
    stalk_on_down = models.SmallIntegerField(default='0')
    stalk_on_unreachable = models.SmallIntegerField(default='0')
    flap_detection_enabled = models.SmallIntegerField(default='0')
    flap_detection_on_up = models.SmallIntegerField(default='0')
    flap_detection_on_down = models.SmallIntegerField(default='0')
    flap_detection_on_unreachable = models.SmallIntegerField(default='0')
    low_flap_threshold = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    high_flap_threshold = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    process_performance_data = models.SmallIntegerField(default='0')
    freshness_checks_enabled = models.SmallIntegerField(default='0')
    freshness_threshold = models.SmallIntegerField(default='0')
    passive_checks_enabled = models.SmallIntegerField(default='0')
    event_handler_enabled = models.SmallIntegerField(default='0')
    active_checks_enabled = models.SmallIntegerField(default='0')
    retain_status_information = models.SmallIntegerField(default='0')
    retain_nonstatus_information = models.SmallIntegerField(default='0')
    notifications_enabled = models.SmallIntegerField(default='0')
    obsess_over_host = models.SmallIntegerField(default='0')
    failure_prediction_enabled = models.SmallIntegerField(default='0')
    notes = models.CharField(max_length=255, default='')
    notes_url = models.CharField(max_length=255, default='')
    icon_image = models.CharField(max_length=255, default='')
    icon_image_alt = models.CharField(max_length=255, default='')
    vrml_image = models.CharField(max_length=255, default='')
    statusmap_image = models.CharField(max_length=255, default='')
    have_2d_coords = models.SmallIntegerField(default='0')
    x_2d = models.SmallIntegerField(default='0')
    y_2d = models.SmallIntegerField(default='0')
    have_3d_coords = models.SmallIntegerField(default='0')
    x_3d = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    y_3d = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    z_3d = models.DecimalField(max_digits=10, decimal_places=2, default='0')

    class Meta:
        db_table = "nagios_hosts"


class HostContactGroups(models.Model):
    host_contactgroup_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    host_id = models.IntegerField(default='0')
    contactgroup_object_id = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_host_contactgroups"


class HostContacts(models.Model):
    host_contact_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    host_id = models.IntegerField(default='0')
    contact_object_id = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_host_contacts"


class HostParenthosts(models.Model):
    host_parenthost_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    host_id = models.IntegerField(default='0')
    parent_host_object_id = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_host_parenthosts"


class HostChecks(models.Model):
    hostcheck_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    host_object_id = models.IntegerField(default='0')
    check_type = models.SmallIntegerField(default='0')
    is_raw_check = models.SmallIntegerField(default='0')
    current_check_attempt = models.SmallIntegerField(default='0')
    max_check_attempts = models.SmallIntegerField(default='0')
    state = models.SmallIntegerField(default='0')
    state_type = models.SmallIntegerField(default='0')
    start_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    start_time_usec = models.IntegerField(default='0')
    end_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    end_time_usec = models.IntegerField(default='0')
    command_object_id = models.IntegerField(default='0')
    command_args = models.CharField(max_length=255, default='')
    command_line = models.CharField(max_length=255, default='')
    timeout = models.SmallIntegerField(default='0')
    early_timeout = models.SmallIntegerField(default='0')
    execution_time = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    latency = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    return_code = models.SmallIntegerField(default='0')
    output = models.CharField(max_length=255, default='')
    long_output = models.TextField(default='')
    perfdata = models.TextField(default='')

    class Meta:
        db_table = "nagios_hostchecks"


class HostDependencies(models.Model):
    hostdependency_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    config_type = models.SmallIntegerField(default='0')
    host_object_id = models.IntegerField(default='0')
    dependent_host_object_id = models.IntegerField(default='0')
    dependency_type = models.SmallIntegerField(default='0')
    inherits_parent = models.SmallIntegerField(default='0')
    timeperiod_object_id = models.IntegerField(default='0')
    fail_on_up = models.SmallIntegerField(default='0')
    fail_on_down = models.SmallIntegerField(default='0')
    fail_on_unreachable = models.SmallIntegerField(default='0')

    class Meta:
        db_table = "nagios_hostdependencies"


class HostEscalations(models.Model):
    hostescalation_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    config_type = models.SmallIntegerField(default='0')
    host_object_id = models.IntegerField(default='0')
    timeperiod_object_id = models.IntegerField(default='0')
    first_notification = models.SmallIntegerField(default='0')
    last_notification = models.SmallIntegerField(default='0')
    notification_interval = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    escalate_on_recovery = models.SmallIntegerField(default='0')
    escalate_on_down = models.SmallIntegerField(default='0')
    escalate_on_unreachable = models.SmallIntegerField(default='0')

    class Meta:
        db_table = "nagios_hostescalations"


class HostEscalationContactGroups(models.Model):
    hostescalation_contactgroup_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    hostescalation_id = models.IntegerField(default='0')
    contactgroup_object_id = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_hostescalation_contactgroups"


class HostEscalationContacts(models.Model):
    hostescalation_contact_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    hostescalation_id = models.IntegerField(default='0')
    contact_object_id = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_hostescalation_contacts"


class HostGroups(models.Model):
    hostgroup_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    config_type = models.SmallIntegerField(default='0')
    hostgroup_object_id = models.IntegerField(default='0')
    alias = models.CharField(max_length=255, default='')

    class Meta:
        db_table = "nagios_hostgroups"


class HostGroupMembers(models.Model):
    hostgroup_member_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    hostgroup_id = models.IntegerField(default='0')
    host_object_id = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_hostgroup_members"


class HostStatus(models.Model):
    hoststatus_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    host_object_id = models.IntegerField(default='0')
    status_update_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    output = models.CharField(max_length=255, default='')
    long_output = models.TextField(default='')
    perfdata = models.TextField(default='')
    current_state = models.SmallIntegerField(default='0')
    has_been_checked = models.SmallIntegerField(default='0')
    should_be_scheduled = models.SmallIntegerField(default='0')
    current_check_attempt = models.SmallIntegerField(default='0')
    max_check_attempts = models.SmallIntegerField(default='0')
    last_check = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    next_check = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    check_type = models.SmallIntegerField(default='0')
    last_state_change = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    last_hard_state_change = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    last_hard_state = models.SmallIntegerField(default='0')
    last_time_up = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    last_time_down = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    last_time_unreachable = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    state_type = models.SmallIntegerField(default='0')
    last_notification = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    next_notification = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    no_more_notifications = models.SmallIntegerField(default='0')
    notifications_enabled = models.SmallIntegerField(default='0')
    problem_has_been_acknowledged = models.SmallIntegerField(default='0')
    acknowledgement_type = models.SmallIntegerField(default='0')
    current_notification_number = models.SmallIntegerField(default='0')
    passive_checks_enabled = models.SmallIntegerField(default='0')
    active_checks_enabled = models.SmallIntegerField(default='0')
    event_handler_enabled = models.SmallIntegerField(default='0')
    flap_detection_enabled = models.SmallIntegerField(default='0')
    is_flapping = models.SmallIntegerField(default='0')
    percent_state_change = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    latency = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    execution_time = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    scheduled_downtime_depth = models.SmallIntegerField(default='0')
    failure_prediction_enabled = models.SmallIntegerField(default='0')
    process_performance_data = models.SmallIntegerField(default='0')
    obsess_over_host = models.SmallIntegerField(default='0')
    modified_host_attributes = models.IntegerField(default='0')
    event_handler = models.CharField(max_length=255, default='')
    check_command = models.CharField(max_length=255, default='')
    normal_check_interval = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    retry_check_interval = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    check_timeperiod_object_id = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_hoststatus"


class LogEntries(models.Model):
    logentry_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    logentry_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    entry_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    entry_time_usec = models.IntegerField(default='0')
    logentry_type = models.IntegerField(default='0')
    logentry_data = models.CharField(max_length=255, default='')
    realtime_data = models.SmallIntegerField(default='0')
    inferred_data_extracted = models.SmallIntegerField(default='0')

    class Meta:
        db_table = "nagios_logentries"


class ProcessEvents(models.Model):
    processevent_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    event_type = models.SmallIntegerField(default='0')
    event_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    event_time_usec = models.IntegerField(default='0')
    process_id = models.IntegerField(default='0')
    program_name = models.CharField(max_length=16, default='')
    program_version = models.CharField(max_length=20, default='')
    program_date = models.CharField(max_length=10, default='')

    class Meta:
        db_table = "nagios_processevents"


class ProgramStatus(models.Model):
    programstatus_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    status_update_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    program_start_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    program_end_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    is_currently_running = models.SmallIntegerField(default='0')
    process_id = models.IntegerField(default='0')
    daemon_mode = models.SmallIntegerField(default='0')
    last_command_check = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    last_log_rotation = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    notifications_enabled = models.SmallIntegerField(default='0')
    active_service_checks_enabled = models.SmallIntegerField(default='0')
    passive_service_checks_enabled = models.SmallIntegerField(default='0')
    active_host_checks_enabled = models.SmallIntegerField(default='0')
    passive_host_checks_enabled = models.SmallIntegerField(default='0')
    event_handlers_enabled = models.SmallIntegerField(default='0')
    flap_detection_enabled = models.SmallIntegerField(default='0')
    failure_prediction_enabled = models.SmallIntegerField(default='0')
    process_performance_data = models.SmallIntegerField(default='0')
    obsess_over_hosts = models.SmallIntegerField(default='0')
    obsess_over_services = models.SmallIntegerField(default='0')
    modified_host_attributes = models.IntegerField(default='0')
    modified_service_attributes = models.IntegerField(default='0')
    global_host_event_handler = models.CharField(max_length=255, default='')
    global_service_event_handler = models.CharField(max_length=255, default='')

    class Meta:
        db_table = "nagios_programstatus"


class RuntimeVariables(models.Model):
    runtimevariable_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    varname = models.CharField(max_length=64, default='')
    varvalue = models.CharField(max_length=255, default='')

    class Meta:
        db_table = "nagios_runtimevariables"


class ScheduledDowntime(models.Model):
    """
    Description:
    This table is used to store current host and service downtime, which may
    either be current in effect or scheduled to begin at a future time.
    Historical scheduled downtime information can be found in the
    downtimehistory table.
    """
    scheduleddowntime_id = models.IntegerField(default='0')
    instance_id = models.SmallIntegerField(default='0')
    downtime_type = models.SmallIntegerField(default='0')
    object_id = models.IntegerField(default='0')
    entry_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    author_name = models.CharField(max_length=64, default='')
    comment_data = models.CharField(max_length=255, default='')
    internal_downtime_id = models.IntegerField(default='0')
    triggered_by_id = models.IntegerField(default='0')
    is_fixed = models.SmallIntegerField(default='0')
    duration = models.IntegerField(default='0')
    scheduled_start_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    scheduled_end_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    was_started = models.SmallIntegerField(default='0')
    actual_start_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    actual_start_time_usec = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_scheduleddowntime"


class Services(models.Model):
    service_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    config_type = models.IntegerField(default='0')
    host_object_id = models.IntegerField(default='0')
    service_object_id = models.IntegerField(default='0')
    display_name = models.CharField(max_length=64, default='')
    importance = models.IntegerField(default='0')
    check_command_object_id = models.IntegerField(default='0')
    check_command_args = models.CharField(max_length=255, default='')
    eventhandler_command_object_id = models.IntegerField(default='0')
    eventhandler_command_args = models.CharField(max_length=255, default='')
    notification_timeperiod_object_id = models.IntegerField(default='0')
    check_timeperiod_object_id = models.IntegerField(default='0')
    failure_prediction_options = models.CharField(max_length=64, default='')
    check_interval = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    retry_interval = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    max_check_attempts = models.SmallIntegerField(default='0')
    first_notification_delay = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    notification_interval = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    notify_on_warning = models.SmallIntegerField(default='0')
    notify_on_unknown = models.SmallIntegerField(default='0')
    notify_on_critical = models.SmallIntegerField(default='0')
    notify_on_recovery = models.SmallIntegerField(default='0')
    notify_on_flapping = models.SmallIntegerField(default='0')
    notify_on_downtime = models.SmallIntegerField(default='0')
    stalk_on_ok = models.SmallIntegerField(default='0')
    stalk_on_warning = models.SmallIntegerField(default='0')
    stalk_on_unknown = models.SmallIntegerField(default='0')
    stalk_on_critical = models.SmallIntegerField(default='0')
    is_volatile = models.SmallIntegerField(default='0')
    flap_detection_enabled = models.SmallIntegerField(default='0')
    flap_detection_on_ok = models.SmallIntegerField(default='0')
    flap_detection_on_warning = models.SmallIntegerField(default='0')
    flap_detection_on_unknown = models.SmallIntegerField(default='0')
    flap_detection_on_critical = models.SmallIntegerField(default='0')
    low_flap_threshold = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    high_flap_threshold = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    process_performance_data = models.SmallIntegerField(default='0')
    freshness_checks_enabled = models.SmallIntegerField(default='0')
    freshness_threshold = models.SmallIntegerField(default='0')
    passive_checks_enabled = models.SmallIntegerField(default='0')
    event_handler_enabled = models.SmallIntegerField(default='0')
    active_checks_enabled = models.SmallIntegerField(default='0')
    retain_status_information = models.SmallIntegerField(default='0')
    retain_nonstatus_information = models.SmallIntegerField(default='0')
    notifications_enabled = models.SmallIntegerField(default='0')
    obsess_over_service = models.SmallIntegerField(default='0')
    failure_prediction_enabled = models.SmallIntegerField(default='0')
    notes = models.CharField(max_length=255, default='')
    notes_url = models.CharField(max_length=255, default='')
    action_url = models.CharField(max_length=255, default='')
    icon_image = models.CharField(max_length=255, default='')
    icon_image_alt = models.CharField(max_length=255, default='')

    class Meta:
        db_table = "nagios_services"


class ServiceContactGroups(models.Model):
    service_contactgroup_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    service_id = models.IntegerField(default='0')
    contactgroup_object_id = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_service_contactgroups"


class ServiceContacts(models.Model):
    service_contact_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    service_id = models.IntegerField(default='0')
    contact_object_id = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_service_contacts"


class ServiceParentServices(models.Model):
    service_parentservice_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    service_id = models.IntegerField(default='0')
    parent_service_object_id = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_service_parentservices"


class ServiceChecks(models.Model):
    servicecheck_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    service_object_id = models.IntegerField(default='0')
    check_type = models.SmallIntegerField(default='0')
    current_check_attempt = models.SmallIntegerField(default='0')
    max_check_attempts = models.SmallIntegerField(default='0')
    state = models.SmallIntegerField(default='0')
    state_type = models.SmallIntegerField(default='0')
    start_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    start_time_usec = models.IntegerField(default='0')
    end_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    end_time_usec = models.IntegerField(default='0')
    command_object_id = models.IntegerField(default='0')
    command_args = models.CharField(max_length=255, default='')
    command_line = models.CharField(max_length=255, default='')
    timeout = models.SmallIntegerField(default='0')
    early_timeout = models.SmallIntegerField(default='0')
    execution_time = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    latency = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    return_code = models.SmallIntegerField(default='0')
    output = models.CharField(max_length=255, default='')
    long_output = models.TextField(default='')
    perfdata = models.TextField(default='')

    class Meta:
        db_table = "nagios_servicechecks"


class ServiceDependencies(models.Model):
    servicedependency_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    config_type = models.SmallIntegerField(default='0')
    service_object_id = models.IntegerField(default='0')
    dependent_service_object_id = models.IntegerField(default='0')
    dependency_type = models.SmallIntegerField(default='0')
    inherits_parent = models.SmallIntegerField(default='0')
    timeperiod_object_id = models.IntegerField(default='0')
    fail_on_on = models.SmallIntegerField(default='0')
    fail_on_warning = models.SmallIntegerField(default='0')
    fail_on_unknown = models.SmallIntegerField(default='0')
    fail_on_critical = models.SmallIntegerField(default='0')

    class Meta:
        db_table = "nagios_servicedependencies"


class ServiceEscalations(models.Model):
    serviceescalation_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    config_type = models.SmallIntegerField(default='0')
    service_object_id = models.IntegerField(default='0')
    timeperiod_object_id = models.IntegerField(default='0')
    first_notification = models.SmallIntegerField(default='0')
    last_notification = models.SmallIntegerField(default='0')
    notification_interval = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    escalate_on_recovery = models.SmallIntegerField(default='0')
    escalate_on_warning = models.SmallIntegerField(default='0')
    escalate_on_unknown = models.SmallIntegerField(default='0')
    escalate_on_critical = models.SmallIntegerField(default='0')

    class Meta:
        db_table = "nagios_serviceescalation"


class ServiceEscalationContactGroups(models.Model):
    serviceescalation_contactgroup_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    serviceescalation_id = models.IntegerField(default='0')
    contactgroup_object_id = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_serviceescalation_contactgroups"


class ServiceEscalationContacts(models.Model):
    serviceescalation_contact_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    serviceescalation_id = models.IntegerField(default='0')
    contact_object_id = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_serviceescalation_contacts"


class ServiceGroups(models.Model):
    servicegroup_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    config_type = models.SmallIntegerField(default='0')
    servicegroup_object_id = models.IntegerField(default='0')
    alias = models.CharField(max_length=255, default='')

    class Meta:
        db_table = "nagios_servicegroups"


class ServiceGroupMembers(models.Model):
    servicegroup_member_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    servicegroup_id = models.IntegerField(default='0')
    service_object_id = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_servicegroup_members"


class ServiceStatus(models.Model):
    servicestatus_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    service_object_id = models.IntegerField(default='0')
    status_update_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    output = models.CharField(max_length=255, default='')
    long_output = models.TextField(null=False, default='')
    perfdata = models.TextField(null=False, default='')
    current_state = models.SmallIntegerField(default='0')
    has_been_checked = models.SmallIntegerField(default='0')
    should_be_scheduled = models.SmallIntegerField(default='0')
    current_check_attempt = models.SmallIntegerField(default='0')
    max_check_attempts = models.SmallIntegerField(default='0')
    last_check = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    next_check = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    check_type = models.SmallIntegerField(default='0')
    last_state_change = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    last_hard_state_change = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    last_hard_state = models.SmallIntegerField(default='0')
    last_time_ok = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    last_time_warning = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    last_time_unknown = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    last_time_critical = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    state_type = models.SmallIntegerField(default='0')
    last_notification = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    next_notification = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    no_more_notifications = models.SmallIntegerField(default='0')
    notifications_enabled = models.SmallIntegerField(default='0')
    problem_has_been_acknowledged = models.SmallIntegerField(default='0')
    acknowledgement_type = models.SmallIntegerField(default='0')
    current_notification_number = models.SmallIntegerField(default='0')
    passive_checks_enabled = models.SmallIntegerField(default='0')
    active_checks_enabled = models.SmallIntegerField(default='0')
    event_handler_enabled = models.SmallIntegerField(default='0')
    flap_detection_enabled = models.SmallIntegerField(default='0')
    is_flapping = models.SmallIntegerField(default='0')
    percent_state_change = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    latency = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    execution_time = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    scheduled_downtime_depth = models.SmallIntegerField(default='0')
    failure_prediction_enabled = models.SmallIntegerField(default='0')
    process_performance_data = models.SmallIntegerField(default='0')
    obsess_over_service = models.SmallIntegerField(default='0')
    modified_service_attributes = models.IntegerField(default='0')
    event_handler = models.CharField(max_length=255, default='')
    check_command = models.CharField(max_length=255, default='')
    normal_check_interval = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    retry_check_interval = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    check_timeperiod_object_id = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_servicestatus"


class StateHistory(models.Model):
    statehistory_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    state_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    state_time_usec = models.IntegerField(default='0')
    object_id = models.IntegerField(default='0')
    state_change = models.SmallIntegerField(default='0')
    state = models.SmallIntegerField(default='0')
    state_type = models.SmallIntegerField(default='0')
    current_check_attempt = models.SmallIntegerField(default='0')
    max_check_attempts = models.SmallIntegerField(default='0')
    last_state = models.SmallIntegerField(default='0')
    last_hard_state = models.SmallIntegerField(default='0')
    output = models.CharField(max_length=255, default='')
    long_output = models.TextField(default='')

    class Meta:
        db_table = "nagios_statehistory"


class SystemCommands(models.Model):
    systemcommand_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    start_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    start_time_usec = models.IntegerField(default='0')
    end_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    end_time_usec = models.IntegerField(default='0')
    command_line = models.CharField(max_length=255, default='')
    timeout = models.SmallIntegerField(default='0')
    early_timeout = models.SmallIntegerField(default='0')
    execution_time = models.DecimalField(max_digits=10, decimal_places=2, default='0')
    return_code = models.SmallIntegerField(default='0')
    output = models.CharField(max_length=255, default='')
    long_output = models.TextField(default='')

    class Meta:
        db_table = "nagios_systemcommands"


class TimedEventQueue(models.Model):
    """
    Description:
    This table is used to store all timed events that are in the Nagios event
    queue, scheduled to be executed at a future time. Historical timed events
    can be found in the timedevents table.

    Values:
        recurring_event:
            0 = Not recurring
            1 = Recurring
    """
    timedeventqueue_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    event_type = models.SmallIntegerField(default='0')
    queued_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    queued_time_usec = models.IntegerField(default='0')
    scheduled_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    recurring_event = models.SmallIntegerField(default='0')
    object_id = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_timedeventqueue"


class TimedEvents(models.Model):
    timedevent_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    event_type = models.SmallIntegerField(default='0')
    queued_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    queued_time_usec = models.IntegerField(default='0')
    event_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    event_time_usec = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    scheduled_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    recurring_event = models.SmallIntegerField(default='0')
    object_id = models.IntegerField(default='0')
    deletion_time = models.DateTimeField(default='0000-00-00 00:00:00', blank=True)
    deletion_time_usec = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_timedevents"


class TimePeriods(models.Model):
    timeperiod_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    config_type = models.SmallIntegerField(default='0')
    timeperiod_object_id = models.IntegerField(default='0')
    alias = models.CharField(max_length=255, default='')

    class Meta:
        db_table = "nagios_timeperiods"


class TimePeriodTimeRanges(models.Model):
    timeperiod_timerange_id = models.AutoField(primary_key=True)
    instance_id = models.SmallIntegerField(default='0')
    timeperiod_id = models.IntegerField(default='0')
    day = models.SmallIntegerField(default='0')
    start_sec = models.IntegerField(default='0')
    end_sec = models.IntegerField(default='0')

    class Meta:
        db_table = "nagios_timeperiod_timeranges"
