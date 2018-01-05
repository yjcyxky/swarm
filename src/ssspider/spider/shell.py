# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import _io
import sys
import os
import subprocess as sp
import inspect

from spider.utils import format
from spider.logging import logger


__author__ = "Johannes Köster"

STDOUT = sys.stdout
if not isinstance(sys.stdout, _io.TextIOWrapper):
    # workaround for nosetest since it overwrites sys.stdout
    # in a strange way that does not work with Popen
    STDOUT = None


class shell:
    _process_args = {}
    _process_prefix = ""
    _process_suffix = ""

    @classmethod
    def executable(cls, cmd):
        if os.path.split(cmd)[-1] == "bash":
            cls._process_prefix = "set -euo pipefail; "
        cls._process_args["executable"] = cmd

    @classmethod
    def prefix(cls, prefix):
        cls._process_prefix = format(prefix, stepout=2)

    @classmethod
    def suffix(cls, suffix):
        cls._process_suffix = format(suffix, stepout=2)

    def __new__(cls, cmd, *args,
                async=False,
                iterable=False,
                read=False, bench_record=None,
                **kwargs):
        if "stepout" in kwargs:
            raise KeyError("Argument stepout is not allowed in shell command.")
        cmd = format(cmd, *args, stepout=2, **kwargs)
        context = inspect.currentframe().f_back.f_locals

        logger.shellcmd(cmd)

        stdout = sp.PIPE if iterable or async or read else STDOUT

        close_fds = sys.platform != 'win32'

        conda_env = context.get("conda_env", None)
        if conda_env is None:
            env_prefix = ""
        else:
            env_prefix = "source activate {};".format(conda_env)
            logger.info("Activating conda environment {}.".format(conda_env))

        proc = sp.Popen("{} {} {} {}".format(
                            env_prefix,
                            cls._process_prefix,
                            cmd.rstrip(),
                            cls._process_suffix),
                        bufsize=-1,
                        shell=True,
                        stdout=stdout,
                        close_fds=close_fds, **cls._process_args)

        ret = None
        if iterable:
            return cls.iter_stdout(proc, cmd)
        if read:
            ret = proc.stdout.read()
        elif async:
            return proc
        if bench_record is not None:
            from spider.benchmark import benchmarked
            # Note: benchmarking does not work in case of async=True
            with benchmarked(proc.pid, bench_record):
                retcode = proc.wait()
        else:
            retcode = proc.wait()
        if retcode:
            raise sp.CalledProcessError(retcode, cmd)
        return ret

    @staticmethod
    def iter_stdout(proc, cmd):
        for l in proc.stdout:
            yield l[:-1].decode()
        retcode = proc.wait()
        if retcode:
            raise sp.CalledProcessError(retcode, cmd)


if "SHELL" in os.environ:
    shell.executable(os.environ["SHELL"])
