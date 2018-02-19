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
    instance_id = models.SmallIntegerField(primary_key=True)
    instance_name = models.CharField(max_length=64)
    instance_description = models.CharField(max_length=128)

    class Meta:
        db_table = "nagios_instances"


class Objects(models.Model):
    object_id = models.IntegerField(primary_key=True)
    instance = models.ForeignKey(Instances, on_delete=True)
    objecttype_id = models.SmallIntegerField()
    name1 = models.CharField(max_length=128)
    name2 = models.CharField(max_length=128, null=True)
    is_active = models.SmallIntegerField()

    class Meta:
        db_table = "nagios_objects"


class Acknowledgements(models.Model):
    acknowledgement_id = models.IntegerField(primary_key=True)
    instance = models.ForeignKey(Instances, on_delete=True)
    entry_time = models.DateTimeField()
    entry_time_usec = models.IntegerField()
    acknowledgement_type = models.SmallIntegerField()
    object = models.ForeignKey(Objects, on_delete=True)
    state = models.SmallIntegerField()
    author_name = models.CharField(max_length=64)
    comment_data = models.CharField(max_length=255)
    is_sticky = models.SmallIntegerField()
    persistent_comment = models.SmallIntegerField()
    notify_contacts = models.SmallIntegerField()

    class Meta:
        db_table = "nagios_acknowledgements"


class Commands(models.Model):

    class Meta:
        db_table = "nagios_commands"


class CommentHistory(models.Model):
    commenthistory_id = models.IntegerField(primary_key=True)
    instance = models.ForeignKey(Instances, on_delete=True)
    entry_time = models.DateTimeField()
    entry_time_usec = models.IntegerField()
    comment_type = models.SmallIntegerField()
    entry_type = models.SmallIntegerField()
    object = models.ForeignKey(Objects, on_delete=True)
    comment_time = models.DateTimeField()
    internal_comment_id = models.IntegerField()
    author_name = models.CharField(max_length=64)
    comment_data = models.CharField(max_length=255)
    is_persistent = models.SmallIntegerField()
    comment_source = models.SmallIntegerField()
    expires = models.SmallIntegerField()
    expiration_time = models.DateTimeField()
    deletion_time = models.DateTimeField()
    deletion_time_usec = models.IntegerField()

    class Meta:
        db_table = "nagios_commenthistory"


class Comments(models.Model):
    comment_id = models.IntegerField(primary_key=True)
    instance = models.ForeignKey(Instances, on_delete=True)
    entry_time = models.DateTimeField()
    entry_time_usec = models.IntegerField()
    commnet_type = models.SmallIntegerField()
    entry_type = models.SmallIntegerField()
    object = models.ForeignKey(Objects, on_delete=True)
    comment_time = models.DateTimeField()
    internal_comment_id = models.IntegerField()
    author_name = models.CharField(max_length=64)
    comment_data = models.CharField(max_length=255)
    is_persistent = models.SmallIntegerField()
    comment_source = models.SmallIntegerField()
    expires = models.SmallIntegerField()
    expiration_time = models.DateTimeField()

    class Meta:
        db_table = "nagios_comments"


class ConfigFiles(models.Model):

    class Meta:
        db_table = "nagios_configfiles"


class ConfigFileVariables(models.Model):

    class Meta:
        db_table = "nagios_configfilevariables"


class ConnInfo(models.Model):

    class Meta:
        db_table = "nagios_conninfo"


class ContactAddresses(models.Model):

    class Meta:
        db_table = "nagios_contact_addresses"


class ContactNotificationCommands(models.Model):

    class Meta:
        db_table = "nagios_contact_notificationcommands"


class ContactGroupMembers(models.Model):

    class Meta:
        db_table = "nagios_contactgroup_members"


class ContactGroups(models.Model):

    class Meta:
        db_table = "nagios_contactgroups"


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
    notification_id = models.IntegerField(primary_key=True)
    instance = models.ForeignKey(Instances, on_delete=True)
    notification_type = models.SmallIntegerField()
    notification_reason = models.SmallIntegerField()
    object = models.ForeignKey(Objects, on_delete=True)
    start_time = models.DateTimeField()
    start_time_usec = models.IntegerField()
    end_time = models.DateTimeField()
    end_time_usec = models.IntegerField()
    state = models.SmallIntegerField()
    output = models.CharField(max_length=255)
    long_output = models.TextField()
    escalated = models.SmallIntegerField()
    contacts_notified = models.SmallIntegerField()
    # New Custom Field
    checked = models.BooleanField(default=False)
    checked_time = models.DateTimeField(null=True)

    class Meta:
        db_table = "nagios_notifications"


class ContactNotifications(models.Model):
    contactnotification_id = models.IntegerField(primary_key=True,
                                                 )
    instance = models.ForeignKey(Instances, on_delete=True)
    notification = models.ForeignKey(Notifications, on_delete=True)
    contact_object = models.ForeignKey(Objects, on_delete=True)
    start_time = models.DateTimeField()
    start_time_usec = models.IntegerField()
    end_time = models.DateTimeField()
    end_time_usec = models.IntegerField()

    class Meta:
        db_table = "nagios_contactnotifications"


class ContactNotificationMethods(models.Model):
    contactnotificationmethod_id = models.IntegerField(primary_key=True,
                                                       )
    instance = models.ForeignKey(Instances, on_delete=True)
    contactnotification = models.ForeignKey(ContactNotifications,
                                            on_delete=True)
    start_time = models.DateTimeField()
    start_time_usec = models.IntegerField()
    end_time = models.DateTimeField()
    end_time_usec = models.IntegerField()
    command_object = models.ForeignKey(Objects, on_delete=True)
    command_args = models.CharField(max_length=255)

    class Meta:
        db_table = "nagios_contactnotificationmethods"


class Contacts(models.Model):

    class Meta:
        db_table = "nagios_contacts"


class ContactStatus(models.Model):

    class Meta:
        db_table = "nagios_contactstatus"


class CustomVariables(models.Model):

    class Meta:
        db_table = "nagios_customvariables"


class CustomVariableStatus(models.Model):
    customvariablestatus = models.IntegerField(primary_key=True)
    instance = models.ForeignKey(Instances, on_delete=True)
    object = models.ForeignKey(Objects, on_delete=True)
    status_update_time = models.DateTimeField()
    has_been_modified = models.IntegerField()
    varname = models.CharField(max_length=255)
    varvalue = models.CharField(max_length=255)

    class Meta:
        db_table = "nagios_customvariablestatus"


class Dbversion(models.Model):

    class Meta:
        db_table = "nagios_dbversion"


class DowntimeHistory(models.Model):
    downtimehistory_id = models.IntegerField(primary_key=True)
    instance = models.ForeignKey(Instances, on_delete=True)
    downtime_type = models.SmallIntegerField()
    object = models.ForeignKey(Objects, on_delete=True)
    entry_time = models.DateTimeField()
    author_name = models.CharField(max_length=64)
    comment_data = models.CharField(max_length=255)
    internal_downtime_id = models.IntegerField()
    triggered_by = models.ForeignKey('DowntimeHistory', on_delete=True)
    is_fixed = models.SmallIntegerField()
    duration = models.SmallIntegerField()
    scheduled_start_time = models.DateTimeField()
    scheduled_end_time = models.DateTimeField()
    was_started = models.SmallIntegerField()
    actual_start_time = models.DateTimeField()
    actual_start_time_usec = models.IntegerField()
    actual_end_time = models.DateTimeField()
    actual_end_time_usec = models.IntegerField()
    was_cancelled = models.SmallIntegerField()

    class Meta:
        db_table = "nagios_downtimehistory"


class EventHandlers(models.Model):
    eventhandler_id = models.IntegerField(primary_key=True)
    instance = models.ForeignKey(Instances, on_delete=True)
    eventhandler_type = models.SmallIntegerField()
    object = models.ForeignKey(Objects, on_delete=True,
                               related_name='eventhandlers_object_id')
    state = models.SmallIntegerField()
    state_type = models.SmallIntegerField()
    start_time = models.DateTimeField()
    start_time_usec = models.IntegerField()
    end_time = models.DateTimeField()
    end_time_usec = models.IntegerField()
    command_object = models.ForeignKey(Objects, on_delete=True,
                                       related_name='eventhandlers_command_object_id')
    command_args = models.CharField(max_length=255)
    command_line = models.CharField(max_length=255)
    timeout = models.SmallIntegerField()
    early_timeout = models.SmallIntegerField()
    execution_time = models.DecimalField(max_digits=10, decimal_places=2)
    return_code = models.SmallIntegerField()
    output = models.CharField(max_length=255)
    long_output = models.TextField()

    class Meta:
        db_table = "nagios_eventhandlers"


class ExternalCommands(models.Model):
    externalcommand_id = models.IntegerField(primary_key=True)
    instance = models.ForeignKey(Instances, on_delete=True)
    entry_time = models.DateTimeField()
    command_type = models.SmallIntegerField()
    command_name = models.CharField(max_length=128)
    command_args = models.CharField(max_length=255)

    class Meta:
        db_table = "nagios_externalcommands"


class FlappingHistory(models.Model):
    flappinghistory_id = models.IntegerField(primary_key=True)
    instance = models.ForeignKey(Instances, on_delete=True)
    event_time = models.DateTimeField()
    event_time_usec = models.IntegerField()
    event_type = models.SmallIntegerField()
    reason_type = models.SmallIntegerField()
    flapping_type = models.SmallIntegerField()
    object = models.ForeignKey(Objects, on_delete=True)
    percent_state_change = models.DecimalField(max_digits=10, decimal_places=2)
    low_threshold = models.DecimalField(max_digits=10, decimal_places=2)
    high_threshold = models.DecimalField(max_digits=10, decimal_places=2)
    comment_time = models.DateTimeField()
    internal_comment_id = models.IntegerField()

    class Meta:
        db_table = "nagios_flappinghistory"


class HostContactGroups(models.Model):

    class Meta:
        db_table = "nagios_host_contactgroups"


class HostContacts(models.Model):

    class Meta:
        db_table = "nagios_host_contacts"


class HostParenthosts(models.Model):

    class Meta:
        db_table = "nagios_host_parenthosts"


class HostChecks(models.Model):
    hostcheck_id = models.IntegerField(primary_key=True)
    instance = models.ForeignKey(Instances, on_delete=True)
    host_object = models.ForeignKey(Objects, on_delete=True,
                                    related_name='hostchecks_host_object_id')
    check_type = models.SmallIntegerField()
    is_raw_check = models.SmallIntegerField()
    current_check_attempt = models.SmallIntegerField()
    max_check_attempts = models.SmallIntegerField()
    state = models.SmallIntegerField()
    state_type = models.SmallIntegerField()
    start_time = models.DateTimeField()
    start_time_usec = models.IntegerField()
    end_time = models.DateTimeField()
    end_time_usec = models.IntegerField()
    command_object = models.ForeignKey(Objects, on_delete=True,
                                       related_name='hostchecks_command_object_id')
    command_args = models.CharField(max_length=255)
    command_line = models.CharField(max_length=255)
    timeout = models.SmallIntegerField()
    early_timeout = models.SmallIntegerField()
    execution_time = models.DecimalField(max_digits=10, decimal_places=2)
    latency = models.DecimalField(max_digits=10, decimal_places=2)
    return_code = models.SmallIntegerField()
    output = models.CharField(max_length=255)
    long_output = models.TextField()
    perfdata = models.TextField()

    class Meta:
        db_table = "nagios_hostchecks"


class HostDependencies(models.Model):

    class Meta:
        db_table = "nagios_hostdependencies"


class HostEscalationContactGroups(models.Model):

    class Meta:
        db_table = "nagios_hostescalation_contactgroups"


class HostEscalationContacts(models.Model):

    class Meta:
        db_table = "nagios_hostescalation_contacts"


class HostEscalations(models.Model):

    class Meta:
        db_table = "nagios_hostescalations"


class HostGroupMembers(models.Model):

    class Meta:
        db_table = "nagios_hostgroup_members"


class HostGroups(models.Model):

    class Meta:
        db_table = "nagios_hostgroups"


class Hosts(models.Model):

    class Meta:
        db_table = "nagios_hosts"


class HostStatus(models.Model):
    hoststatus_id = models.IntegerField(primary_key=True)
    instance = models.ForeignKey(Instances, on_delete=True)
    host_object = models.ForeignKey(Objects, on_delete=True,
                                    related_name='hoststatus_host_object_id')
    status_update_time = models.DateTimeField()
    output = models.CharField(max_length=255)
    long_output = models.TextField()
    perfdata = models.TextField()
    current_state = models.SmallIntegerField()
    has_been_checked = models.SmallIntegerField()
    should_be_scheduled = models.SmallIntegerField()
    current_check_attempt = models.SmallIntegerField()
    max_check_attempts = models.SmallIntegerField()
    last_check = models.DateTimeField()
    next_check = models.DateTimeField()
    check_type = models.SmallIntegerField()
    last_state_change = models.DateTimeField()
    last_hard_state_change = models.DateTimeField()
    last_hard_state = models.SmallIntegerField()
    last_time_up = models.DateTimeField()
    last_time_down = models.DateTimeField()
    last_time_unreachable = models.DateTimeField()
    state_type = models.SmallIntegerField()
    last_notification = models.DateTimeField()
    next_notification = models.DateTimeField()
    no_more_notifications = models.SmallIntegerField()
    notifications_enabled = models.SmallIntegerField()
    problem_has_been_acknowledged = models.SmallIntegerField()
    acknowledgement_type = models.SmallIntegerField()
    current_notification_number = models.SmallIntegerField()
    passive_checks_enabled = models.SmallIntegerField()
    active_checks_enabled = models.SmallIntegerField()
    event_handler_enabled = models.SmallIntegerField()
    flap_detection_enabled = models.SmallIntegerField()
    is_flapping = models.SmallIntegerField()
    percent_state_change = models.DecimalField(max_digits=10, decimal_places=2)
    latency = models.DecimalField(max_digits=10, decimal_places=2)
    execution_tme = models.DecimalField(max_digits=10, decimal_places=2)
    scheduled_downtime_depth = models.SmallIntegerField()
    failure_prediction_enabled = models.SmallIntegerField()
    process_performance_data = models.SmallIntegerField()
    obsess_over_host = models.SmallIntegerField()
    modified_host_attributes = models.IntegerField()
    event_handler = models.CharField(max_length=255)
    check_command = models.CharField(max_length=255)
    normal_check_interval = models.DecimalField(max_digits=10, decimal_places=2)
    retry_check_interval = models.DecimalField(max_digits=10, decimal_places=2)
    check_timeperiod_object = models.ForeignKey(Objects, on_delete=True,
                                                related_name='hoststatus_check_timeperiod_object_id')

    class Meta:
        db_table = "nagios_hoststatus"


class LogEntries(models.Model):
    logentry_id = models.IntegerField(primary_key=True)
    instance = models.ForeignKey(Instances, on_delete=True)
    logentry_time = models.DateTimeField()
    entry_time = models.DateTimeField()
    entry_time_usec = models.IntegerField()
    logentry_type = models.IntegerField()
    logentry_data = models.CharField(max_length=255)
    realtime_data = models.SmallIntegerField()
    inferred_data_extracted = models.SmallIntegerField()

    class Meta:
        db_table = "nagios_logentries"


class ProcessEvents(models.Model):
    processevent_id = models.IntegerField(primary_key=True)
    instance = models.ForeignKey(Instances, on_delete=True)
    event_type = models.SmallIntegerField()
    event_time = models.DateTimeField()
    event_time_usec = models.IntegerField()
    process_id = models.IntegerField()
    program_name = models.CharField(max_length=16)
    program_version = models.CharField(max_length=20)
    program_date = models.CharField(max_length=10)

    class Meta:
        db_table = "nagios_processevents"


class ProgramStatus(models.Model):
    programstatus_id = models.IntegerField(primary_key=True)
    instance = models.ForeignKey(Instances, on_delete=True)
    status_update_time = models.DateTimeField()
    program_start_time = models.DateTimeField()
    program_end_time = models.DateTimeField()
    is_currently_running = models.SmallIntegerField()
    process_id = models.IntegerField()
    daemon_mode = models.SmallIntegerField()
    last_command_check = models.DateTimeField()
    last_log_rotation = models.DateTimeField()
    notifications_enabled = models.SmallIntegerField()
    active_service_checks_enabled = models.SmallIntegerField()
    passive_service_checks_enabled = models.SmallIntegerField()
    active_host_checks_enabled = models.SmallIntegerField()
    passive_host_checks_enabled = models.SmallIntegerField()
    event_handlers_enabled = models.SmallIntegerField()
    flap_detection_enabled = models.SmallIntegerField()
    failure_prediction_enabled = models.SmallIntegerField()
    process_performance_data = models.SmallIntegerField()
    obsess_over_hosts = models.SmallIntegerField()
    obsess_over_services = models.SmallIntegerField()
    modified_host_attributes = models.IntegerField()
    modified_service_attributes = models.IntegerField()
    global_host_event_handler = models.CharField(max_length=255)
    global_service_event_handler = models.CharField(max_length=255)

    class Meta:
        db_table = "nagios_programstatus"


class RuntimeVariables(models.Model):
    runtimevariable_id = models.IntegerField(primary_key=True)
    instance = models.ForeignKey(Instances, on_delete=True)
    varname = models.CharField(max_length=64)
    varvalue = models.CharField(max_length=255)

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
    scheduleddowntime_id = models.IntegerField()
    instance = models.ForeignKey(Instances, on_delete=True)
    downtime_type = models.SmallIntegerField()
    object = models.ForeignKey(Objects, on_delete=True)
    entry_time = models.DateTimeField()
    author_name = models.CharField(max_length=64)
    comment_data = models.CharField(max_length=255)
    internal_downtime_id = models.IntegerField()
    triggered_by_id = models.IntegerField()
    is_fixed = models.SmallIntegerField()
    duration = models.IntegerField()
    scheduled_start_time = models.DateTimeField()
    scheduled_end_time = models.DateTimeField()
    was_started = models.SmallIntegerField()
    actual_start_time = models.DateTimeField()
    actual_start_time_usec = models.IntegerField()

    class Meta:
        db_table = "nagios_scheduleddowntime"


class ServiceContactGroups(models.Model):

    class Meta:
        db_table = "nagios_service_contactgroups"


class ServiceContacts(models.Model):

    class Meta:
        db_table = "nagios_service_contacts"


class ServiceParentServices(models.Model):

    class Meta:
        db_table = "nagios_service_parentservices"


class ServiceChecks(models.Model):
    servicecheck_id = models.IntegerField(primary_key=True)
    instance = models.ForeignKey(Instances, on_delete=True)
    service_object = models.ForeignKey(Objects, on_delete=True,
                                       related_name='servicechecks_service_object_id')
    check_type = models.SmallIntegerField()
    current_check_attempt = models.SmallIntegerField()
    max_check_attempts = models.SmallIntegerField()
    state = models.SmallIntegerField()
    state_type = models.SmallIntegerField()
    start_time = models.DateTimeField()
    start_time_usec = models.IntegerField()
    end_time = models.DateTimeField()
    end_time_usec = models.IntegerField()
    command_object = models.ForeignKey(Objects, on_delete=True,
                                       related_name='servicechecks_command_object_id')
    command_args = models.CharField(max_length=255)
    command_line = models.CharField(max_length=255)
    timeout = models.SmallIntegerField()
    early_timeout = models.SmallIntegerField()
    execution_time = models.DecimalField(max_digits=10, decimal_places=2)
    latency = models.DecimalField(max_digits=10, decimal_places=2)
    return_code = models.SmallIntegerField()
    output = models.CharField(max_length=255)
    long_output = models.TextField()
    perfdata = models.TextField()

    class Meta:
        db_table = "nagios_servicechecks"


class ServiceDependencies(models.Model):

    class Meta:
        db_table = "nagios_servicedependencies"


class ServiceEscalationContactGroups(models.Model):

    class Meta:
        db_table = "nagios_serviceescalation_contactgroups"


class ServiceEscalationContacts(models.Model):

    class Meta:
        db_table = "nagios_serviceescalation_contacts"


class ServiceEscalations(models.Model):

    class Meta:
        db_table = "nagios_serviceescalation"


class ServiceGroupMembers(models.Model):

    class Meta:
        db_table = "nagios_servicegroup_members"


class ServiceGroups(models.Model):

    class Meta:
        db_table = "nagios_servicegroups"


class Services(models.Model):

    class Meta:
        db_table = "nagios_services"


class ServiceStatus(models.Model):
    servicestatus_id = models.IntegerField(primary_key=True)
    instance = models.ForeignKey(Instances, on_delete=True)
    service_object = models.ForeignKey(Objects, on_delete=True,
                                       related_name='servicestatus_service_object_id')
    status_update_time = models.DateTimeField()
    output = models.CharField(max_length=255)
    long_output = models.TextField(null=False)
    perfdata = models.TextField(null=False)
    current_state = models.SmallIntegerField()
    has_been_checked = models.SmallIntegerField()
    should_be_scheduled = models.SmallIntegerField()
    current_check_attempt = models.SmallIntegerField()
    max_check_attempts = models.SmallIntegerField()
    last_check = models.DateTimeField()
    next_check = models.DateTimeField()
    check_type = models.SmallIntegerField()
    last_state_change = models.DateTimeField()
    last_hard_state_change = models.DateTimeField()
    last_hard_state = models.SmallIntegerField()
    last_time_ok = models.DateTimeField()
    last_time_warning = models.DateTimeField()
    last_time_unknown = models.DateTimeField()
    last_time_critical = models.DateTimeField()
    state_type = models.SmallIntegerField()
    last_notification = models.DateTimeField()
    next_notification = models.DateTimeField()
    no_more_notifications = models.SmallIntegerField()
    notifications_enabled = models.SmallIntegerField()
    problem_has_been_acknowledged = models.SmallIntegerField()
    acknowledgement_type = models.SmallIntegerField()
    current_notification_number = models.SmallIntegerField()
    passive_checks_enabled = models.SmallIntegerField()
    active_checks_enabled = models.SmallIntegerField()
    event_handler_enabled = models.SmallIntegerField()
    flap_detection_enabled = models.SmallIntegerField()
    is_flapping = models.SmallIntegerField()
    percent_state_change = models.DecimalField(max_digits=10, decimal_places=2)
    latency = models.DecimalField(max_digits=10, decimal_places=2)
    execution_time = models.DecimalField(max_digits=10, decimal_places=2)
    scheduled_downtime_depth = models.SmallIntegerField()
    failure_prediction_enabled = models.SmallIntegerField()
    process_performance_data = models.SmallIntegerField()
    obsess_over_service = models.SmallIntegerField()
    modified_service_attributes = models.IntegerField()
    event_handler = models.CharField(max_length=255)
    check_command = models.CharField(max_length=255)
    normal_check_interval = models.DecimalField(max_digits=10, decimal_places=2)
    retry_check_interval = models.DecimalField(max_digits=10, decimal_places=2)
    check_timeperiod_object = models.ForeignKey(Objects, on_delete=True,
                                                related_name='servicestatus_check_timeperiod_object_id')

    class Meta:
        db_table = "nagios_servicestatus"


class StateHistory(models.Model):
    statehistory_id = models.IntegerField(primary_key=True)
    instance = models.ForeignKey(Instances, on_delete=True)
    state_time = models.DateTimeField()
    state_time_usec = models.IntegerField()
    object = models.ForeignKey(Objects, on_delete=True)
    state_change = models.SmallIntegerField()
    state = models.SmallIntegerField()
    state_type = models.SmallIntegerField()
    current_check_attempt = models.SmallIntegerField()
    max_check_attempts = models.SmallIntegerField()
    last_state = models.SmallIntegerField()
    last_hard_state = models.SmallIntegerField()
    output = models.CharField(max_length=255)
    long_output = models.TextField()

    class Meta:
        db_table = "nagios_statehistory"


class SystemCommands(models.Model):
    systemcommand_id = models.IntegerField(primary_key=True)
    instance = models.ForeignKey(Instances, on_delete=True)
    start_time = models.DateTimeField()
    start_time_usec = models.IntegerField()
    end_time = models.DateTimeField()
    end_time_usec = models.IntegerField()
    command_line = models.CharField(max_length=255)
    timeout = models.SmallIntegerField()
    early_timeout = models.SmallIntegerField()
    execution_tme = models.DecimalField(max_digits=10, decimal_places=2)
    return_code = models.SmallIntegerField()
    output = models.CharField(max_length=255)
    long_output = models.TextField()

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
    timedeventqueue_id = models.IntegerField(primary_key=True)
    instance = models.ForeignKey(Instances, on_delete=True)
    event_type = models.SmallIntegerField()
    queued_time = models.DateTimeField()
    queued_time_usec = models.IntegerField()
    scheduled_time = models.DateTimeField()
    recurring_event = models.SmallIntegerField()
    object = models.ForeignKey(Objects, on_delete=True)

    class Meta:
        db_table = "nagios_timedeventqueue"


class TimedEvents(models.Model):
    timedevent_id = models.IntegerField(primary_key=True)
    instance = models.ForeignKey(Instances, on_delete=True)
    event_type = models.SmallIntegerField()
    queued_time = models.DateTimeField()
    queued_time_usec = models.IntegerField()
    event_time = models.DateTimeField()
    event_time_usec = models.DateTimeField()
    scheduled_time = models.DateTimeField()
    recurring_event = models.SmallIntegerField()
    object = models.ForeignKey(Objects, on_delete=True)
    deletion_time = models.DateTimeField()
    deletion_time_usec = models.IntegerField()

    class Meta:
        db_table = "nagios_timedevents"


class TimePeriodTimeRanges(models.Model):

    class Meta:
        db_table = "nagios_timeperiod_timeranges"


class TimePeriods(models.Model):

    class Meta:
        db_table = "nagios_timeperiods"
