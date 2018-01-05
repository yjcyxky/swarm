# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import os
import posixpath

from spider.script import script


def is_script(path):
    return path.endswith("wrapper.py") or path.endswith("wrapper.R")


def get_path(path, prefix=None):
    if not (path.startswith("http") or path.startswith("file:")):
        if prefix is None:
            prefix = "https://bitbucket.org/spider/spider-wrappers/raw/"
        path = prefix + path
    return path


def get_script(path, prefix=None):
    path = get_path(path, prefix=prefix)
    if not is_script(path):
        path += "/wrapper.py"
    return path


def get_conda_env(path, prefix=None):
    path = get_path(path, prefix=prefix)
    if is_script(path):
        # URLs and posixpaths share the same separator. Hence use posixpath here.
        path = posixpath.dirname(path)
    return path + "/environment.yaml"


def wrapper(path, input, output, params, wildcards, threads, resources, log, config, rulename, conda_env, bench_record, prefix):
    """
    Load a wrapper from https://bitbucket.org/spider/spider-wrappers under
    the given path + wrapper.py and execute it.
    """
    path = get_script(path, prefix=prefix)
    script(path, "", input, output, params, wildcards, threads, resources, log, config, rulename, conda_env, bench_record)
