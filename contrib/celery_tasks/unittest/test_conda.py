import sys, os
from os import path

sys.path.append(path.dirname(path.dirname(os.getcwd())))
import logging, os, json
from cobweb.celery_tasks.conda_api import CondaError, CondaEnvExistsError, set_root_prefix
from cobweb.celery_tasks.conda_api import create as conda_create
from cobweb.celery_tasks.conda_api import install as conda_install

def get_config():
    config = {}
    working_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    with open(os.path.join(working_dir, "config.json"), "r") as f:
        config.update(json.load(f))
    return config

def _set_conda_prefix():
    config = get_config()
    TASK_SETTINGS = config.get("TASK_SETTINGS")
    CONDA_ROOT_PREFIX = TASK_SETTINGS.get("conda_root_prefix")
    set_root_prefix(CONDA_ROOT_PREFIX)

def install_package(pkg_name = None, version = None):
    _set_conda_prefix()
    try:
        pkg_env = "%s-%s" % (pkg_name, version)
        pkgs = ("%s=%s" % (pkg_name, version), )
        result = conda_create(name = pkg_env, pkgs = pkgs)
        print(result)
    except CondaEnvExistsError as e:
        result = conda_install(name = pkg_env, pkgs = pkgs)
        print(result)
    except CondaError as e:
        pass

if __name__ == '__main__':
    install_package(pkg_name = "samtools", version = "0.1.16")
