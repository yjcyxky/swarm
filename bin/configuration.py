# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import copy
import errno
import logging
import os
import sys
import subprocess
import warnings

# 必须将scouts添加到sys.path中
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from collections import OrderedDict
from configparser import ConfigParser
from exceptions import ScoutsConfigException

HEADER = """\
 -------------------------------
 < Hi, My name is Scouts-{version} >
 -------------------------------
        \   ^__^
         \  (oo)\_______
            (__)\       )\/\\
                ||----w||
                ||     ||

 Scouts is designed by {company_name} Company for HPC Users...
"""

# the prefix to append to gunicorn worker processes after init
GUNICORN_WORKER_READY_PREFIX = "[ready] "

try:
    from cryptography.fernet import Fernet
except ImportError:
    pass


def generate_fernet_key():
    try:
        FERNET_KEY = Fernet.generate_key().decode()
    except NameError:
        FERNET_KEY = "cryptography_not_found_storing_passwords_in_plain_text"
    return FERNET_KEY


def expand_env_var(env_var):
    """
    Expands (potentially nested) env vars by repeatedly applying
    `expandvars` and `expanduser` until interpolation stops having
    any effect.
    """
    if not env_var:
        return env_var
    while True:
        interpolated = os.path.expanduser(os.path.expandvars(str(env_var)))
        if interpolated == env_var:
            return interpolated
        else:
            env_var = interpolated


DEFAULT_CONFIG = """\
[core]
# The home folder for Scouts, default is ~/scouts
scouts_home = {SCOUTS_HOME}

# Database
scouts_db_engine = django.db.backends.mysql
scouts_db_name = scouts
scouts_db_user = root
scouts_db_password = yjc040653
scouts_db_host = localhost
scouts_db_port = 3306

# Turn unit test mode on (overwrites many configuration options with test
# values at runtime)
unit_test_mode = False
# Run_mode only supports the following modes: DEBUG|INFO|WARNING|ERROR
run_mode = DEBUG

[webserver]
# The base url of your website as airflow cannot guess what domain or
# cname you are using. This is used in automated emails that
# airflow sends to point links to the right web server
base_url = http://localhost:8080

# The ip specified when starting the web server
web_server_host = 0.0.0.0

# The port on which to run the web server
web_server_port = 8080

# Paths to the SSL certificate and key for the web server. When both are
# provided SSL will be enabled. This does not change the web server port.
web_server_ssl_cert =
web_server_ssl_key =

# Number of seconds the gunicorn webserver waits before timing out on a worker
web_server_worker_timeout = 120

# Number of workers to refresh at a time. When set to 0, worker refresh is
# disabled. When nonzero, airflow periodically refreshes webserver workers by
# bringing up new ones and killing old ones.
worker_refresh_batch_size = 1

# Number of seconds to wait before refreshing a batch of workers.
worker_refresh_interval = 30

# Secret key used to run your django app
secret_key = {FERNET_KEY}

# Number of workers to run the Gunicorn web server
workers = 4

# The worker class gunicorn should use. Choices include
# sync (default), eventlet, gevent
worker_class = sync

# Log files for the gunicorn webserver. '-' means log to stderr.
access_logfile = -
error_logfile = -

# Expose the configuration file in the web server
expose_config = False

# Set to true to turn on authentication:
# http://pythonhosted.org/airflow/security.html#web-authentication
authenticate = False

# Filter the list of dags by owner name (requires authentication to be enabled)
filter_by_owner = False

# Filtering mode. Choices include user (default) and ldapgroup.
# Ldap group filtering requires using the ldap backend
#
# Note that the ldap server needs the "memberOf" overlay to be set up
# in order to user the ldapgroup mode.
owner_mode = user

# Default DAG orientation. Valid values are:
# LR (Left->Right), TB (Top->Bottom), RL (Right->Left), BT (Bottom->Top)
dag_orientation = LR

# Puts the webserver in demonstration mode; blurs the names of Operators for
# privacy.
demo_mode = False

# The amount of time (in secs) webserver will wait for initial handshake
# while fetching logs from other worker machine
log_fetch_timeout_sec = 5

# By default, the webserver shows paused DAGs. Flip this to hide paused
# DAGs by default
hide_paused_dags_by_default = False

[celery]
# This section only applies if you are using the CeleryExecutor in
# [core] section above

# The app name that will be used by celery
celery_app_name = airflow.executors.celery_executor

# The concurrency that will be used when starting workers with the
# "airflow worker" command. This defines the number of task instances that
# a worker will take, so size up your workers based on the resources on
# your worker box and the nature of your tasks
celeryd_concurrency = 16

# When you start an airflow worker, airflow starts a tiny web server
# subprocess to serve the workers local log files to the airflow main
# web server, who then builds pages and sends them to users. This defines
# the port on which the logs are served. It needs to be unused, and open
# visible from the main web server to connect into the workers.
worker_log_server_port = 8793

# The Celery broker URL. Celery supports RabbitMQ, Redis and experimentally
# a sqlalchemy database. Refer to the Celery documentation for more
# information.
broker_url = sqla+mysql://airflow:airflow@localhost:3306/airflow

# Another key Celery setting
celery_result_backend = db+mysql://airflow:airflow@localhost:3306/airflow

# Celery Flower is a sweet UI for Celery. Airflow has a shortcut to start
# it `airflow flower`. This defines the IP that Celery Flower runs on
flower_host = 0.0.0.0

# This defines the port that Celery Flower runs on
flower_port = 5555

# Default queue that tasks get assigned to and that worker listen on.
default_queue = default
"""

TEST_CONFIG = """\
[core]
scouts_home = {SCOUTS_HOME}
unit_test_mode = True
scouts_db_engine = django.db.backends.mysql
scouts_db_name = scouts
scouts_db_user = root
scouts_db_password = yjc040653
scouts_db_host = localhost
scouts_db_port = 3306
run_mode = DEBUG

[webserver]
base_url = http://localhost:8080
web_server_host = 0.0.0.0
web_server_port = 8080
dag_orientation = LR
log_fetch_timeout_sec = 5
hide_paused_dags_by_default = False

[celery]
celery_app_name = airflow.executors.celery_executor
celeryd_concurrency = 16
worker_log_server_port = 8793
broker_url = sqla+mysql://airflow:airflow@localhost:3306/airflow
celery_result_backend = db+mysql://airflow:airflow@localhost:3306/airflow
flower_host = 0.0.0.0
flower_port = 5555
default_queue = default

"""


class ScoutsConfigParser(ConfigParser):
    def __init__(self, *args, **kwargs):
        ConfigParser.__init__(self, *args, **kwargs)
        self.read_string(parameterized_config(DEFAULT_CONFIG))
        self.is_validated = False

    def read_string(self, string, source='<string>'):
        """
        Read configuration from a string.
        """
        ConfigParser.read_string(self, string, source=source)

    def _validate(self):
        RUNMODE = self.get('core', 'run_mode')
        if RUNMODE is None:
            raise ScoutsConfigException("You must specified run_mode in core section.")

        self.is_validated = True

    def _get_env_var_option(self, section, key):
        # must have format AIRFLOW__{SECTION}__{KEY} (note double underscore)
        env_var = 'SCOUTS__{S}__{K}'.format(S=section.upper(), K=key.upper())
        if env_var in os.environ:
            return expand_env_var(os.environ[env_var])

    def get(self, section, key, **kwargs):
        section = str(section).lower()
        key = str(key).lower()

        # first check environment variables
        option = self._get_env_var_option(section, key)
        if option is not None:
            return option

        # ...then the config file
        if self.has_option(section, key):
            return expand_env_var(
                ConfigParser.get(self, section, key, **kwargs))


    def getboolean(self, section, key):
        val = str(self.get(section, key)).lower().strip()
        if '#' in val:
            val = val.split('#')[0].strip()
        if val.lower() in ('t', 'true', '1'):
            return True
        elif val.lower() in ('f', 'false', '0'):
            return False
        else:
            raise ScoutsConfigException(
                'The value for configuration option "{}:{}" is not a '
                'boolean (received "{}").'.format(section, key, val))

    def getint(self, section, key):
        return int(self.get(section, key))

    def getfloat(self, section, key):
        return float(self.get(section, key))

    def read(self, filenames):
        ConfigParser.read(self, filenames)
        self._validate()

    def as_dict(self, display_source=False, display_sensitive=False):
        """
        Returns the current configuration as an OrderedDict of OrderedDicts.
        :param display_source: If False, the option value is returned. If True,
            a tuple of (option_value, source) is returned. Source is either
            'airflow.cfg' or 'default'.
        :type display_source: bool
        :param display_sensitive: If True, the values of options set by env
            vars and bash commands will be displayed. If False, those options
            are shown as '< hidden >'
        :type display_sensitive: bool
        """
        cfg = copy.deepcopy(self._sections)

        # remove __name__ (affects Python 2 only)
        for options in cfg.values():
            options.pop('__name__', None)

        # add source
        if display_source:
            for section in cfg:
                for k, v in cfg[section].items():
                    cfg[section][k] = (v, 'scouts config')

        # add env vars and overwrite because they have priority
        for ev in [ev for ev in os.environ if ev.startswith('SCOUTS__')]:
            try:
                _, section, key = ev.split('__')
                opt = self._get_env_var_option(section, key)
            except ValueError:
                opt = None
            if opt:
                if (
                        not display_sensitive
                        and ev != 'SCOUTS__CORE__UNIT_TEST_MODE'):
                    opt = '< hidden >'
                if display_source:
                    opt = (opt, 'env var')
                cfg.setdefault(section.lower(), OrderedDict()).update(
                    {key.lower(): opt})

        return cfg

    def load_test_config(self):
        """
        Load the unit test configuration.

        Note: this is not reversible.
        """
        # override any custom settings with defaults
        self.read_string(parameterized_config(DEFAULT_CONFIG))
        # then read test config
        self.read_string(parameterized_config(TEST_CONFIG))
        # then read any "custom" test settings
        self.read(TEST_CONFIG_FILE)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise ScoutsConfigException('Had trouble creating a directory')


# Setting SCOUTS_HOME and SCOUTS_CONFIG from environment variables, using
# "~/scouts" and "~/scouts/scouts.cfg" respectively as defaults.

if 'SCOUTS_HOME' not in os.environ:
    SCOUTS_HOME = expand_env_var('~/scouts')
    SCOUTS_LOG = os.path.join(SCOUTS_HOME, 'logs')
else:
    SCOUTS_HOME = expand_env_var(os.environ['SCOUTS_HOME'])
    SCOUTS_LOG = os.path.join(SCOUTS_HOME, 'logs')

mkdir_p(SCOUTS_HOME)
mkdir_p(SCOUTS_LOG)

if 'SCOUTS_CONFIG' not in os.environ:
    if os.path.isfile(expand_env_var('~/scouts.cfg')):
        SCOUTS_CONFIG = expand_env_var('~/scouts.cfg')
    else:
        SCOUTS_CONFIG = SCOUTS_HOME + '/scouts.cfg'
else:
    SCOUTS_CONFIG = expand_env_var(os.environ['SCOUTS_CONFIG'])

def parameterized_config(template):
    """
    Generates a configuration from the provided template + variables defined in
    current scope
    :param template: a config content templated with {{variables}}
    """
    FERNET_KEY = generate_fernet_key()
    all_vars = {k: v for d in [globals(), locals()] for k, v in d.items()}
    return template.format(**all_vars)

TEST_CONFIG_FILE = SCOUTS_HOME + '/unittests.cfg'
if not os.path.isfile(TEST_CONFIG_FILE):
    logging.info("Creating new airflow config file for unit tests in: " +
                 TEST_CONFIG_FILE)
    with open(TEST_CONFIG_FILE, 'w') as f:
        f.write(parameterized_config(TEST_CONFIG))

if not os.path.isfile(SCOUTS_CONFIG):
    # These configuration options are used to generate a default configuration
    # when it is missing. The right way to change your configuration is to
    # alter your configuration file, not this code.
    logging.info("Creating new airflow config file in: " + SCOUTS_CONFIG)
    with open(SCOUTS_CONFIG, 'w') as f:
        f.write(parameterized_config(DEFAULT_CONFIG))

logging.info("Reading the config from " + SCOUTS_CONFIG)


conf = ScoutsConfigParser()
conf.read(SCOUTS_CONFIG)


def load_test_config():
    """
    Load the unit test configuration.

    Note: this is not reversible.
    """
    conf.load_test_config()

if conf.getboolean('core', 'unit_test_mode'):
    load_test_config()


def get(section, key, **kwargs):
    return conf.get(section, key, **kwargs)


def getboolean(section, key):
    return conf.getboolean(section, key)


def getfloat(section, key):
    return conf.getfloat(section, key)


def getint(section, key):
    return conf.getint(section, key)


def has_option(section, key):
    return conf.has_option(section, key)


def remove_option(section, option):
    return conf.remove_option(section, option)


def as_dict(display_source=False, display_sensitive=False):
    return conf.as_dict(
        display_source=display_source, display_sensitive=display_sensitive)
as_dict.__doc__ = conf.as_dict.__doc__


def set(section, option, value):  # noqa
    return conf.set(section, option, value)
