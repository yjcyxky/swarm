#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

from __future__ import print_function
from __future__ import absolute_import
import logging
import os
import sys
import subprocess
import threading
import textwrap
import psutil
import argparse
import daemon
import time
import signal

import configuration as conf
import manage

from collections import namedtuple
from django.core.management import call_command
from django.core.management.commands import loaddata
from daemon.pidfile import TimeoutPIDLockFile

from configuration import conf as settings
from version import (get_version, get_company_name)
from exceptions import SwarmException
from ssspider.spider import get_argument_parser, main as spider_main


def sigint_handler(sig, frame):
    sys.exit(0)


def setup_django():
    # set the default Django settings module for the initdb function,
    # otherwise raise django.core.exceptions.AppRegistryNotReady.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swarm.settings')
    # Setup django project
    try:
        import django
    except ImportError:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        )
    django.setup()


def initdb(args, **kwargs):
    print("初始化数据库...")
    setup_django()
    call_command('makemigrations', verbosity = 0, interactive = False)
    call_command('migrate', verbosity = 0)
    initdata = args.initdata
    if initdata:
        call_command(loaddata.Command(), initdata, verbosity = 0)
    print("完成.")


def ganglia(args, **kwargs):
    print("初始化Ganglia数据库...")
    setup_django()
    from ssganglia.models import RRDConfig
    rrd_dir_path = args.rrd_dir_path and args.rrd_dir_path or \
                   settings.get('ganglia', 'rrd_dir_path')
    print("rrd目录路径: %s" % rrd_dir_path)
    if rrd_dir_path:
        ganglia_config = RRDConfig(rrd_dir_path)
        ganglia_config.sync2db()
    print("完成.")


def resetdb(args, **kwargs):
    print("DB: " + repr())
    if args.yes or input(
            "This will drop existing tables if they exist. "
            "Proceed? (y/n)").upper() == "Y":
        pass
        # db_utils.resetdb()
    else:
        print("Bail.")


def spider(args, **kwargs):
    from ssspider.exceptions import SpiderParameterError
    from ssspider.utils import gen_spider_file
    spider_template = args.spider_template
    vars_file_path = args.ini
    spiderfile = args.spiderfile

    if spider_template is None and vars_file_path is None:
        spider_main(args = args)

    if not (spider_template and vars_file_path):
        raise SpiderParameterError("You must specify spider_template(-st or --spider_template)"
                                   "and ini arguments(-i or --ini) or only specify spiderfile argument(--spiderfile).")
    else:
        workdir = args.directory
        if workdir:
            if not os.path.exists(workdir):
                print(
                    "Creating specified working directory {}.".format(workdir))
                os.makedirs(workdir)
            workdir = os.path.abspath(workdir)
            os.chdir(workdir)
        else:
            workdir = os.getcwd()
        spiderfile = gen_spider_file(spider_template, vars_file_path, output_dir=workdir)
        args.spiderfile = spiderfile
        spider_main(args = args)


def flower(args, **kwargs):
    broker_url = conf.get('celery', 'BROKER_URL')
    broker = '--b={}'.format(broker_url)
    address = '--address={}'.format(args.hostname)
    port = '--port={}'.format(args.port)
    flower_cmd = ['flower', broker, address, port]

    if args.broker_api:
        api = '--broker_api=' + args.broker_api
        flower_cmd.append(api)

    if args.flower_conf:
        flower_conf = '--conf=' + args.flower_conf
        flower_cmd.append(flower_conf)

    if args.persistent:
        persistent = '--persistent=' + str(args.persistent)
        flower_db  = '--db=%s' % os.path.join(conf.BASE_DIR, 'flower')
        flower_cmd.append(persistent)
        flower_cmd.append(flower_db)

    extra_args = kwargs.get('extra_args')
    if extra_args:
        flower_cmd.extend(extra_args)

    if args.auth:
        # It doesn't work, because cannot get password text from djano.
        # How to solve it?
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "swarm.settings")
        try:
            import django
            django.setup()
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        from django.contrib.auth.models import User
        users = User.objects.filter(is_active = True).all()
        user_passwd = ''
        for user in users:
            username = user.username
            password = user.password
            user_passwd = user_passwd + '%s:%s,' % (username, password)
        basic_auth = '--basic_auth=%s' % user_passwd
        flower_cmd.append(basic_auth)

    # 去除重复输入的参数，取最后一个
    print('Flower CMD: %s' % str(flower_cmd))
    flower_cmd = list(set(flower_cmd))
    print('Flower CMD(Unique): %s' % str(flower_cmd))
    if args.daemon:
        pid, stdout, stderr, log_file = setup_locations("flower", args.pid, args.stdout, args.stderr, args.log_file)
        stdout = open(stdout, 'w+')
        stderr = open(stderr, 'w+')

        ctx = daemon.DaemonContext(
            pidfile=TimeoutPIDLockFile(pid, -1),
            stdout=stdout,
            stderr=stderr,
        )

        with ctx:
            os.execvp("flower", flower_cmd)

        stdout.close()
        stderr.close()
    else:
        signal.signal(signal.SIGINT, sigint_handler)
        signal.signal(signal.SIGTERM, sigint_handler)

        os.execvp("flower", flower_cmd)


def celery(args, **kwargs):
    BASE_DIR = conf.BASE_DIR
    env = {}
    env.update({
        'PYTHONPATH': BASE_DIR,
        'PATH': os.environ.get('PATH'),
    })

    celery_cmd = ['celery', '-A', args.module_name, 'worker', '--loglevel=%s' % args.loglevel]

    if args.daemon:
        pid, stdout, stderr, logfile = setup_locations("celery-beat", args.pid, args.stdout, args.stderr, args.log_file)
        celery_cmd.extend(['--pidfile=%s' % pid, '--detach', '--logfile=%s' % logfile])

        os.execvpe("celery", celery_cmd, env)
    else:
        signal.signal(signal.SIGINT, sigint_handler)
        signal.signal(signal.SIGTERM, sigint_handler)

        os.execvpe("celery", celery_cmd, env)


def celery_beat(args, **kwargs):
    BASE_DIR = conf.BASE_DIR
    env = {}
    env.update({
        'PYTHONPATH': BASE_DIR,
        'PATH': os.environ.get('PATH'),
    })

    celery_cmd = ['celery', '-A', args.module_name, 'beat', '--loglevel=%s' % args.loglevel]
    if args.django_beat:
        celery_cmd.append('--scheduler=django_celery_beat.schedulers:DatabaseScheduler')
    else:
        schedule_file = os.path.join(os.path.expanduser(conf.SWARM_HOME), "swarm-celery-beat-schedule.db")
        celery_cmd.append('--schedule=%s' % schedule_file)

    if args.daemon:
        pid, stdout, stderr, logfile = setup_locations("celery-beat", args.pid, args.stdout, args.stderr, args.log_file)
        celery_cmd.extend(['--pidfile=%s' % pid, '--detach', '--logfile=%s' % logfile])

        os.execvpe("celery-beat", celery_cmd, env)
    else:
        signal.signal(signal.SIGINT, sigint_handler)
        signal.signal(signal.SIGTERM, sigint_handler)

        os.execvpe("celery-beat", celery_cmd, env)


def setup_locations(process, pid=None, stdout=None, stderr=None, log=None):
    if not stderr:
        stderr = os.path.join(os.path.expanduser(conf.SWARM_LOG), "swarm-{}.err".format(process))
    if not stdout:
        stdout = os.path.join(os.path.expanduser(conf.SWARM_LOG), "swarm-{}.out".format(process))
    if not log:
        log = os.path.join(os.path.expanduser(conf.SWARM_LOG), "swarm-{}.log".format(process))
    if not pid:
        pid = os.path.join(os.path.expanduser(conf.SWARM_HOME), "swarm-{}.pid".format(process))

    return pid, stdout, stderr, log


def restart_workers(gunicorn_master_proc, num_workers_expected):
    """
    Runs forever, monitoring the child processes of @gunicorn_master_proc and
    restarting workers occasionally.

    Each iteration of the loop traverses one edge of this state transition
    diagram, where each state (node) represents
    [ num_ready_workers_running / num_workers_running ]. We expect most time to
    be spent in [n / n]. `bs` is the setting webserver.worker_refresh_batch_size.

    The horizontal transition at ? happens after the new worker parses all the
    dags (so it could take a while!)

       V ────────────────────────────────────────────────────────────────────────┐
    [n / n] ──TTIN──> [ [n, n+bs) / n + bs ]  ────?───> [n + bs / n + bs] ──TTOU─┘
       ^                          ^───────────────┘
       │
       │      ┌────────────────v
       └──────┴────── [ [0, n) / n ] <─── start

    We change the number of workers by sending TTIN and TTOU to the gunicorn
    master process, which increases and decreases the number of child workers
    respectively. Gunicorn guarantees that on TTOU workers are terminated
    gracefully and that the oldest worker is terminated.
    """

    def wait_until_true(fn):
        """
        Sleeps until fn is true
        """
        while not fn():
            time.sleep(0.1)

    def get_num_workers_running(gunicorn_master_proc):
        workers = psutil.Process(gunicorn_master_proc.pid).children()
        return len(workers)

    def get_num_ready_workers_running(gunicorn_master_proc):
        workers = psutil.Process(gunicorn_master_proc.pid).children()
        ready_workers = [
            proc for proc in workers
            if conf.GUNICORN_WORKER_READY_PREFIX in proc.cmdline()[0]
        ]
        return len(ready_workers)

    def start_refresh(gunicorn_master_proc):
        batch_size = conf.getint('webserver', 'worker_refresh_batch_size')
        logging.debug('%s doing a refresh of %s workers',
                      state, batch_size)
        sys.stdout.flush()
        sys.stderr.flush()

        excess = 0
        for _ in range(batch_size):
            gunicorn_master_proc.send_signal(signal.SIGTTIN)
            excess += 1
            wait_until_true(lambda: num_workers_expected + excess ==
                            get_num_workers_running(gunicorn_master_proc))

    wait_until_true(lambda: num_workers_expected ==
                    get_num_workers_running(gunicorn_master_proc))

    while True:
        num_workers_running = get_num_workers_running(gunicorn_master_proc)
        num_ready_workers_running = get_num_ready_workers_running(gunicorn_master_proc)

        state = '[{0} / {1}]'.format(num_ready_workers_running, num_workers_running)

        # Whenever some workers are not ready, wait until all workers are ready
        if num_ready_workers_running < num_workers_running:
            logging.debug('%s some workers are starting up, waiting...', state)
            sys.stdout.flush()
            time.sleep(1)

        # Kill a worker gracefully by asking gunicorn to reduce number of workers
        elif num_workers_running > num_workers_expected:
            excess = num_workers_running - num_workers_expected
            logging.debug('%s killing %s workers', state, excess)

            for _ in range(excess):
                gunicorn_master_proc.send_signal(signal.SIGTTOU)
                excess -= 1
                wait_until_true(lambda: num_workers_expected + excess ==
                                get_num_workers_running(gunicorn_master_proc))

        # Start a new worker by asking gunicorn to increase number of workers
        elif num_workers_running == num_workers_expected:
            refresh_interval = conf.getint('webserver', 'worker_refresh_interval')
            logging.debug(
                '%s sleeping for %ss starting doing a refresh...',
                state, refresh_interval
            )
            time.sleep(refresh_interval)
            start_refresh(gunicorn_master_proc)

        else:
            # num_ready_workers_running == num_workers_running < num_workers_expected
            logging.error((
                "%s some workers seem to have died and gunicorn"
                "did not restart them as expected"
            ), state)
            time.sleep(10)
            if len(
                psutil.Process(gunicorn_master_proc.pid).children()
            ) < num_workers_expected:
                start_refresh(gunicorn_master_proc)


def advisor(args, **kwargs):
    from ssadvisor.jobs import Job
    bash_templ_path = args.bash_template
    vars_file_path = args.ini
    jobid = jobname = args.job
    terminate_flag = args.terminate_flag

    if (jobname and bash_templ_path and vars_file_path):
        job = Job(jobname, bash_templ_path = bash_templ_path, vars_file_path = vars_file_path)
        job.submit_job()
        print('Your job has been submitted with ID %s' % job.get_jobid())
    elif (jobid and terminate_flag):
        job = Job(jobid = jobid)
        jobstatus = job.terminate_job()
        print("The status of your job is: %s" % jobstatus)
    else:
        job = Job(jobid = jobid)
        jobstatus = job.get_jobstatus()
        print("The status of your job is %s" % jobstatus)


def webserver(args, **kwargs):
    access_logfile = args.access_logfile or settings.get('webserver', 'access_logfile')
    error_logfile = args.error_logfile or settings.get('webserver', 'error_logfile')
    num_workers = args.workers or settings.get('webserver', 'workers')
    worker_timeout = (args.worker_timeout or
                      settings.get('webserver', 'webserver_worker_timeout'))
    ssl_cert = args.ssl_cert or conf.get('webserver', 'web_server_ssl_cert')
    ssl_key = args.ssl_key or conf.get('webserver', 'web_server_ssl_key')
    if not ssl_cert and ssl_key:
        raise SwarmException(
            'An SSL certificate must also be provided for use with ' + ssl_key)
    if ssl_cert and not ssl_key:
        raise SwarmException(
            'An SSL key must also be provided for use with ' + ssl_cert)

    RUNMODE = settings.get('core', 'run_mode').strip("'\"")
    if args.debug:
        cmd = sys.argv[0]
        subcommand = 'runserver'
        args = [cmd, subcommand, '%s:%s' % (args.hostname, args.port)]
        django_cmd(args)
    else:
        pid, stdout, stderr, log_file = setup_locations("webserver", pid=args.pid)
        print(
            textwrap.dedent('''\
                Running the Gunicorn Server with:
                Workers: {num_workers} {args.workerclass}
                Host: {args.hostname}:{args.port}
                Timeout: {worker_timeout}
                Logfiles: {access_logfile} {error_logfile}
                PID: {pid}
                =================================================================\
            '''.format(**locals())))

        GUNICORN_CONFIG = os.path.join(conf.BASE_DIR, 'bin', 'gunicorn_config.py')
        run_args = [
            'gunicorn',
            '-w', str(num_workers),
            '-k', str(args.workerclass),
            '-t', str(worker_timeout),
            '-b', args.hostname + ':' + str(args.port),
            '-n', 'swarm-webserver',
            '-p', str(pid),
            '-c', GUNICORN_CONFIG
        ]

        if args.access_logfile:
            run_args += ['--access-logfile', str(args.access_logfile)]

        if args.error_logfile:
            run_args += ['--error-logfile', str(args.error_logfile)]

        if args.daemon:
            run_args += ["-D"]
        if ssl_cert:
            run_args += ['--certfile', ssl_cert, '--keyfile', ssl_key]

        run_args += ["wsgi:application"]

        gunicorn_master_proc = subprocess.Popen(run_args)

        def kill_proc(dummy_signum, dummy_frame):
            gunicorn_master_proc.terminate()
            gunicorn_master_proc.wait()
            sys.exit(0)

        signal.signal(signal.SIGINT, kill_proc)
        signal.signal(signal.SIGTERM, kill_proc)

        # These run forever until SIG{INT, TERM, KILL, ...} signal is sent
        if settings.getint('webserver', 'worker_refresh_interval') > 0:
            restart_workers(gunicorn_master_proc, num_workers)
        else:
            while True:
                time.sleep(1)


def django_cmd(args):
    manage.run(args = args)


def version(args, **kwargs):
    print(conf.HEADER.format(version = get_version(), company_name = get_company_name()))


Arg = namedtuple(
    'Arg', ['flags', 'help', 'action', 'default', 'nargs', 'type', 'choices', 'metavar', 'required'])
Arg.__new__.__defaults__ = (None, None, None, None, None, None, None, None)


class CLIFactory(object):
    args = {
        'pid': Arg(
            ("--pid", ), "PID file location",
            nargs='?'),
        'daemon': Arg(
            ("-D", "--daemon"), "Daemonize instead of running"
                                "in the foreground",
            "store_true"),
        'stderr': Arg(
            ("--stderr", ), "Redirect stderr to this file"),
        'stdout': Arg(
            ("--stdout", ), "Redirect stdout to this file"),
        'log_file': Arg(
            ("-l", "--log-file"), "Location of the log file"),
        # webserver
        'port': Arg(
            ("-p", "--port"),
            default=conf.get('webserver', 'WEB_SERVER_PORT'),
            type=int,
            help="The port on which to run the server"),
        'ssl_cert': Arg(
            ("--ssl_cert", ),
            default=conf.get('webserver', 'WEB_SERVER_SSL_CERT'),
            help="Path to the SSL certificate for the webserver"),
        'ssl_key': Arg(
            ("--ssl_key", ),
            default=conf.get('webserver', 'WEB_SERVER_SSL_KEY'),
            help="Path to the key to use with the SSL certificate"),
        'workers': Arg(
            ("-w", "--workers"),
            default=conf.get('webserver', 'WORKERS'),
            type=int,
            help="Number of workers to run the webserver on"),
        'workerclass': Arg(
            ("-k", "--workerclass"),
            default=conf.get('webserver', 'WORKER_CLASS'),
            choices=['sync', 'eventlet', 'gevent', 'tornado'],
            help="The worker class to use for Gunicorn"),
        'worker_timeout': Arg(
            ("-t", "--worker_timeout"),
            default=conf.get('webserver', 'WEB_SERVER_WORKER_TIMEOUT'),
            type=int,
            help="The timeout for waiting on webserver workers"),
        'hostname': Arg(
            ("-hn", "--hostname"),
            default=conf.get('webserver', 'WEB_SERVER_HOST'),
            help="Set the hostname on which to run the web server"),
        'debug': Arg(
            ("-d", "--debug"),
            "Use the server that ships with Flask in debug mode",
            "store_true"),
        'access_logfile': Arg(
            ("-A", "--access_logfile"),
            default=conf.get('webserver', 'ACCESS_LOGFILE'),
            help="The logfile to store the webserver access log. Use '-' to print to "
                 "stderr."),
        'error_logfile': Arg(
            ("-E", "--error_logfile"),
            default=conf.get('webserver', 'ERROR_LOGFILE'),
            help="The logfile to store the webserver error log. Use '-' to print to "
                 "stderr."),
        # initdb
        'initdata': Arg(
            ("-I", "--initdata"),
            help="The init data for initializing database."),
        # resetdb
        'yes': Arg(
            ("-y", "--yes"),
            "Do not prompt to confirm reset. Use with care!",
            "store_true",
            default=False),
        # flower
        'broker_api': Arg(("-a", "--broker_api"), help="Broker api"),
        'flower_hostname': Arg(
            ("-hn", "--hostname"),
            default=conf.get('celery', 'FLOWER_HOST'),
            help="Set the hostname on which to run the server"),
        'flower_port': Arg(
            ("-p", "--port"),
            default=conf.get('celery', 'FLOWER_PORT'),
            type=int,
            help="The port on which to run the server"),
        'flower_conf': Arg(
            ("-fc", "--flower_conf"),
            help="Configuration file for flower"),
        'task_params': Arg(
            ("-tp", "--task_params"),
            help="Sends a JSON params dict to the task"),
        'persistent': Arg(
            ("-P", "--persistent"),
            "Enable persistent mode (default False).",
            "store_true",
            default = False),
        'auth': Arg(
            ("-au", "--auth"),
            "Enable auth mode (default False).",
            "store_true",
            default = False),
        # celery
        'module_name': Arg(
            ("-m", "--module_name"),
            default = 'swarm',
            help="The name of the current module for Celery. Default Value: swarm"),
        'django_beat': Arg(
            ("-b", "--django-beat"),
            "Use django_celery_beat database as a backend.",
            "store_true",
            default = False),
        'loglevel': Arg(
            ("-L", "--loglevel"),
            help = "Logging level, choose between DEBUG, INFO, WARNING,"
                   "ERROR, CRITICAL, or FATAL.",
            default = 'INFO'),
        # advisor
        'bash_template': Arg(
            ("-bt", "--bash_template"),
            help="bash template file for submitting job(Only Support Jinja2 Syntax).",
            required = False),
        'vars_file': Arg(
            ("-i", "--ini"),
            help="config file for rendering template file(Only Support INI Syntax).",
            required = False),
        'terminate_flag': Arg(
            ("-T", "--terminate"),
            "Terminate the specified job.",
            "store_true",
            default = False),
        'job': Arg(
            ("job",),
            help="job's name or id."),
        # spider
        'spider_template': Arg(
            ("-st", "--spider_template"),
            help="spider template file",
            required=False),
        'rrd_dir_path': Arg(
            ("-rrd", "--rrd_dir_path"),
            help="RRD Directory Path.",
            required=True)
    }
    subparsers = (
        {
            'func': initdb,
            'help': "Initialize the metadata database",
            'args': ('initdata',),
        }, {
            'func': webserver,
            'help': "Start a swarm webserver instance",
            'args': ('port', 'workers', 'workerclass', 'worker_timeout', 'hostname',
                     'pid', 'daemon', 'stdout', 'stderr', 'access_logfile',
                     'error_logfile', 'log_file', 'ssl_cert', 'ssl_key', 'debug'),
        }, {
            'func': resetdb,
            'help': "Burn down and rebuild the metadata database",
            'args': ('yes',),
        }, {
            'func': flower,
            'help': "Start a Celery Flower",
            'args': ('flower_hostname', 'flower_port', 'flower_conf', 'broker_api',
                     'pid', 'daemon', 'stdout', 'stderr', 'log_file', 'persistent', 'auth'),
        }, {
            'func': celery,
            'help': "Start a Celery Worker",
            'args': ('module_name', 'pid', 'daemon', 'log_file', 'loglevel'),
        }, {
            'func': celery_beat,
            'help': "Start a Celery Beat",
            'args': ('module_name', 'pid', 'daemon', 'log_file', 'django_beat', 'loglevel'),
        }, {
            'func': version,
            'help': "Show the version",
            'args': tuple(),
        }, {
            'func': advisor,
            'help': "Submit a job to cluster. (Advisor Terminal Version)",
            'args': ('bash_template', 'vars_file', 'terminate_flag', 'job'),
        }, {
            'func': spider,
            'help': "Spider is a Python based language and execution "
                    "environment for GNU Make-like workflows.(Spider Terminal Version)",
            # 调用外部命令时使用，external_args与extra_args联用，extra_args用于扩展外部命令的参数
            'extra_args': ('spider_template', 'vars_file'),
            'external_args': True
        }, {
            'func': ganglia,
            'help': "Initialized Ganglia Database.",
            'args': ('rrd_dir_path',),
        }

    )
    subparsers_dict = {sp['func'].__name__: sp for sp in subparsers}

    @classmethod
    def get_parser(cls):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(
            help='sub-command help', dest='subcommand')
        subparsers.required = True

        subparser_list = cls.subparsers_dict.keys()
        for sub in subparser_list:
            sub = cls.subparsers_dict[sub]
            sp = subparsers.add_parser(sub['func'].__name__, help=sub['help'])
            sp.set_defaults(func=sub['func'])
            if sub.get('external_args'):
                get_argument_parser(parser = sp)
                for arg in sub['extra_args']:
                    arg = cls.args[arg]
                    kwargs = {
                        f: getattr(arg, f)
                        for f in arg._fields if f != 'flags' and getattr(arg, f)}
                    sp.add_argument(*arg.flags, **kwargs)
            else:
                for arg in sub['args']:
                    arg = cls.args[arg]
                    kwargs = {
                        f: getattr(arg, f)
                        for f in arg._fields if f != 'flags' and getattr(arg, f)}
                    sp.add_argument(*arg.flags, **kwargs)
        return parser


def get_parser():
    return CLIFactory.get_parser()
