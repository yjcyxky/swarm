from __future__ import absolute_import, unicode_literals
from celery import Task
import logging
from .conda_api import CondaError, CondaEnvExistsError, set_root_prefix
from .conda_api import create as conda_create
from .conda_api import remove as conda_remove
from .conda_api import install as conda_install
from .celery import app, get_config

def _set_conda_prefix():
    config = get_config()
    TASK_SETTINGS = config.get("TASK_SETTINGS")
    CONDA_ROOT_PREFIX = TASK_SETTINGS.get("conda_root_prefix")
    set_root_prefix(CONDA_ROOT_PREFIX)

def get_custom_logger(task_id):
    config = get_config()
    TASK_SETTINGS = config.get("TASK_SETTINGS")
    LOGDIR = TASK_SETTINGS.get("logdir")
    LOGLEVEL = TASK_SETTINGS.get("loglevel")
    logger = logging.getLogger(task_id)
    logger.setLevel(LOGLEVEL)
    handler = logging.FileHandler(os.path.join(LOGDIR, task_id + '.log'), 'w')
    logger.addHandler(handler)
    return logger

class PackageTask(Task):
    def on_success(self, retval, task_id, args, kwargs):
        print("Task %s(Success): %s" % (task_id, retval))
        return super(PackageTask, self).on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        print("Task %s(Failed): %s" % (task_id, exc))
        return super(PackageTask, self).on_failure(exc, task_id, args, kwargs, einfo)

@app.task(base = PackageTask, name = 'install-package', typing=False)
def install_package(pkg_name = None, version = None, *args, **kwargs):
    _set_conda_prefix()
    task_id = install_package.request.id
    # task_logger = get_custom_logger(task_id)
    try:
        pkg_env = "%s-%s" % (pkg_name, version)
        pkgs = ("%s=%s" % (pkg_name, version), )
        result = conda_create(name = pkg_env, pkgs = pkgs)
        # task_logger.info("Create Environment: %s" % pkg_env)
        # task_logger.info("Install Packages: %s" % str(pkgs))
        return str(result) if result else "%s-%s doesn't match any package." % (pkg_name, version)
    except CondaEnvExistsError as e:
        # Environment已经存在时
        result = conda_install(name = pkg_env, pkgs = pkgs)
        return str(result) if result else "%s-%s doesn't match any package." % (pkg_name, version)
        # task_logger.warn("Warning：%s" % str(e))
    except CondaError as e:
        # task_logger.error("CondaError: %s" % str(e))
        pass

@app.task(base = PackageTask, name = 'remove-package', typing=False)
def remove_package(pkg_name = None, version = None, *args, **kwargs):
    _set_conda_prefix()
    task_id = remove_package.request.id
    try:
        pkg_env = '%s-%s' % (pkg_name, version)
        pkgs = (pkg_name, )
        # all = True will remove all environment.
        result = conda_remove(*pkgs, name = pkg_env, all = True)
        if result:
            return str(result) if result else "%s-%s doesn't match any package." % (pkg_name, version)
    except CondaError as e:
        pass
    except Exception as e:
        pass

@app.task(base = PackageTask, name = 'reinstall-package', typing=False)
def reinstall_package(pkg_name = None, version = None, *args, **kwargs):
    _set_conda_prefix()
    task_id = reinstall_package.request.id
    try:
        pkg_env = '%s-%s' % (pkg_name, version)
        removed_pkgs = (pkg_name, )
        installed_pkgs = ("%s=%s" % (pkg_name, version), )
        result = conda_remove(*removed_pkgs, name = pkg_env, all = True)
        print(result)
        if result and result.get("success"):
            try:
                result = conda_create(name = pkg_env, pkgs = installed_pkgs)
                return str(result) if result else "%s-%s doesn't match any package." % (pkg_name, version)
            except CondaEnvExistsError as e:
                # Environment已经存在时
                result = conda_install(name = pkg_env, pkgs = installed_pkgs)
                return str(result) if result else "%s-%s doesn't match any package." % (pkg_name, version)
            except CondaError as e:
                pass
    except CondaError as e:
        pass
    except Exception as e:
        pass
