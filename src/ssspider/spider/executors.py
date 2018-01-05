# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import os
import sys
import contextlib
import time
import datetime
import json
import textwrap
import stat
import shutil
import shlex
import threading
import concurrent.futures
import subprocess
import signal
from functools import partial
from itertools import chain
from collections import namedtuple
from tempfile import mkdtemp
import random
import base64
import uuid

from spider.jobs import Job
from spider.shell import shell
from spider.logging import logger
from spider.stats import Stats
from spider.utils import format, Unformattable, makedirs
from spider.io import get_wildcard_names, Wildcards
from spider.exceptions import print_exception, get_exception_origin
from spider.exceptions import format_error, RuleException, log_verbose_traceback
from spider.exceptions import ClusterJobException, ProtectedOutputException, WorkflowError, ImproperShadowException, SpawnedJobError
from spider.common import Mode
from spider.version import __version__


def format_files(job, io, dynamicio):
    for f in io:
        if f in dynamicio:
            yield "{} (dynamic)".format(f.format_dynamic())
        else:
            yield f


class AbstractExecutor:
    def __init__(self, workflow, dag,
                 printreason=False,
                 quiet=False,
                 printshellcmds=False,
                 printthreads=True,
                 latency_wait=3,
                 benchmark_repeats=1):
        self.workflow = workflow
        self.dag = dag
        self.quiet = quiet
        self.printreason = printreason
        self.printshellcmds = printshellcmds
        self.printthreads = printthreads
        self.latency_wait = latency_wait
        self.benchmark_repeats = benchmark_repeats

    def get_default_remote_provider_args(self):
        if self.workflow.default_remote_provider:
            return (
                " --default-remote-provider {} "
                "--default-remote-prefix {} ").format(
                    self.workflow.default_remote_provider.__module__.split(".")[-1],
                    self.workflow.default_remote_prefix)
        return ""

    def run(self, job,
            callback=None,
            submit_callback=None,
            error_callback=None):
        job.check_protected_output()
        self._run(job)
        callback(job)

    def shutdown(self):
        pass

    def cancel(self):
        pass

    def _run(self, job):
        self.printjob(job)

    def rule_prefix(self, job):
        return "local " if self.workflow.is_local(job.rule) else ""

    def printjob(self, job):
        # skip dynamic jobs that will be "executed" only in dryrun mode
        if self.dag.dynamic(job):
            return

        priority = self.dag.priority(job)
        logger.job_info(jobid=self.dag.jobid(job),
                        msg=job.message,
                        name=job.rule.name,
                        local=self.workflow.is_local(job.rule),
                        input=list(format_files(job, job.input,
                                                job.dynamic_input)),
                        output=list(format_files(job, job.output,
                                                 job.dynamic_output)),
                        log=list(job.log),
                        benchmark=job.benchmark,
                        wildcards=job.wildcards_dict,
                        reason=str(self.dag.reason(job)),
                        resources=job.resources,
                        priority="highest"
                        if priority == Job.HIGHEST_PRIORITY else priority,
                        threads=job.threads)

        if job.dynamic_output:
            logger.info("Subsequent jobs will be added dynamically "
                        "depending on the output of this rule")

    def print_job_error(self, job, msg=None, **kwargs):
        logger.job_error(name=job.rule.name,
                         jobid=self.dag.jobid(job),
                         output=list(format_files(job, job.output,
                                                  job.dynamic_output)),
                         log=list(job.log),
                         aux=kwargs)
        if msg is not None:
            logger.error(msg)

    def handle_job_success(self, job):
        pass

    def handle_job_error(self, job):
        pass


class DryrunExecutor(AbstractExecutor):
    def _run(self, job):
        super()._run(job)
        logger.shellcmd(job.shellcmd)


class RealExecutor(AbstractExecutor):
    def __init__(self, workflow, dag,
                 printreason=False,
                 quiet=False,
                 printshellcmds=False,
                 latency_wait=3,
                 benchmark_repeats=1,
                 assume_shared_fs=True):
        super().__init__(workflow, dag,
                         printreason=printreason,
                         quiet=quiet,
                         printshellcmds=printshellcmds,
                         latency_wait=latency_wait,
                         benchmark_repeats=benchmark_repeats)
        self.assume_shared_fs = assume_shared_fs
        self.stats = Stats()
        self.spiderfile = workflow.spiderfile

    def _run(self, job, callback=None, error_callback=None):
        super()._run(job)
        self.stats.report_job_start(job)
        try:
            self.workflow.persistence.started(job)
        except IOError as e:
            logger.info(
                "Failed to set marker file for job started ({}). "
                "Spider will work, but cannot ensure that output files "
                "are complete in case of a kill signal or power loss. "
                "Please ensure write permissions for the "
                "directory {}".format(e, self.workflow.persistence.path))

    def handle_job_success(self, job, upload_remote=True, ignore_missing_output=False):
        if self.assume_shared_fs:
            self.dag.handle_touch(job)
            self.dag.handle_log(job)
            self.dag.check_and_touch_output(
                job,
                wait=self.latency_wait,
                ignore_missing_output=ignore_missing_output)
            self.dag.unshadow_output(job)
            self.dag.handle_remote(job, upload=upload_remote)
            self.dag.handle_protected(job)
            job.close_remote()
        self.dag.handle_temp(job)

        self.stats.report_job_end(job)
        try:
            self.workflow.persistence.finished(job)
        except IOError as e:
            logger.info("Failed to remove marker file for job started "
                        "({}). Please ensure write permissions for the "
                        "directory {}".format(e,
                                              self.workflow.persistence.path))

    def handle_job_error(self, job, upload_remote=True):
        if self.assume_shared_fs:
            self.dag.handle_log(job, upload_remote=upload_remote)
            job.close_remote()

    def format_job_pattern(self, pattern, job=None, **kwargs):
        overwrite_workdir = []
        if self.workflow.overwrite_workdir:
            overwrite_workdir.extend(("--directory", self.workflow.overwrite_workdir))

        overwrite_config = []
        if self.workflow.overwrite_configfile:
            overwrite_config.extend(("--configfile", self.workflow.overwrite_configfile))
        if self.workflow.config_args:
            overwrite_config.append("--config")
            overwrite_config.extend(self.workflow.config_args)

        printshellcmds = ""
        if self.workflow.printshellcmds:
            printshellcmds = "-p"

        target = job.output if job.output else job.rule.name

        return format(pattern,
                      job=job,
                      attempt=job.attempt,
                      overwrite_workdir=overwrite_workdir,
                      overwrite_config=overwrite_config,
                      printshellcmds=printshellcmds,
                      workflow=self.workflow,
                      spiderfile=self.spiderfile,
                      cores=self.cores,
                      benchmark_repeats=self.benchmark_repeats,
                      target=target,
                      **kwargs)


class TouchExecutor(RealExecutor):
    def run(self, job,
            callback=None,
            submit_callback=None,
            error_callback=None):
        super()._run(job)
        try:
            #Touching of output files will be done by handle_job_success
            time.sleep(0.1)
            callback(job)
        except OSError as ex:
            print_exception(ex, self.workflow.linemaps)
            error_callback(job)

    def handle_job_success(self, job):
        super().handle_job_success(job, ignore_missing_output=True)


_ProcessPoolExceptions = (KeyboardInterrupt, )
try:
    from concurrent.futures.process import BrokenProcessPool
    _ProcessPoolExceptions = (KeyboardInterrupt, BrokenProcessPool)
except ImportError:
    pass


class CPUExecutor(RealExecutor):
    def __init__(self, workflow, dag, workers,
                 printreason=False,
                 quiet=False,
                 printshellcmds=False,
                 use_threads=False,
                 latency_wait=3,
                 benchmark_repeats=1,
                 cores=1):
        super().__init__(workflow, dag,
                         printreason=printreason,
                         quiet=quiet,
                         printshellcmds=printshellcmds,
                         latency_wait=latency_wait,
                         benchmark_repeats=benchmark_repeats)

        self.exec_job = '\\\n'.join((
            'cd {workflow.workdir_init} && ',
            '{sys.executable} -m spider {target} --spiderfile {spiderfile} ',
            '--force -j{cores} --keep-target-files --keep-shadow --keep-remote ',
            '--benchmark-repeats {benchmark_repeats} --attempt {attempt} ',
            '--force-use-threads --wrapper-prefix {workflow.wrapper_prefix} ',
            self.get_default_remote_provider_args(),
            '{overwrite_workdir} {overwrite_config} ',
            '--notemp --quiet --no-hooks --nolock --mode {} '.format(Mode.subprocess)))

        if self.workflow.use_conda:
            self.exec_job += " --use-conda "
            if self.workflow.conda_prefix:
                self.exec_job += " --conda-prefix " + self.workflow.conda_prefix + " "

        self.use_threads = use_threads
        self.cores = cores
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=workers)

    def run(self, job,
            callback=None,
            submit_callback=None,
            error_callback=None):
        super()._run(job)

        if self.use_threads or (not job.is_shadow and (job.is_shell or job.is_norun or job.is_script or job.is_wrapper)):
            job.prepare()
            conda_env = None
            if self.workflow.use_conda:
                conda_env = job.conda_env

            benchmark = None
            if job.benchmark is not None:
                benchmark = str(job.benchmark)
            future = self.pool.submit(
                run_wrapper, job.rule, job.input.plainstrings(),
                job.output.plainstrings(), job.params, job.wildcards, job.threads,
                job.resources, job.log.plainstrings(), benchmark,
                self.benchmark_repeats, conda_env,
                self.workflow.linemaps, self.workflow.debug,
                shadow_dir=job.shadow_dir)
        else:
            # run directive jobs are spawned into subprocesses
            future = self.pool.submit(self.spawn_job, job)

        future.add_done_callback(partial(self._callback, job, callback,
                                         error_callback))

    def spawn_job(self, job):
        exec_job = self.exec_job
        if not job.rule.is_branched:
            exec_job += " --allowed-rules {}".format(job.rule)
        cmd = self.format_job_pattern(exec_job, job=job, _quote_all=True)
        try:
            subprocess.check_call(cmd, shell=True)
        except subprocess.CalledProcessError:
            raise SpawnedJobError()

    def shutdown(self):
        self.pool.shutdown()

    def cancel(self):
        self.pool.shutdown()

    def _callback(self, job, callback, error_callback, future):
        try:
            ex = future.exception()
            if ex:
                raise ex
            callback(job)
        except _ProcessPoolExceptions:
            self.handle_job_error(job)
            # no error callback, just silently ignore the interrupt as the main scheduler is also killed
        except SpawnedJobError:
            # don't print error message, this is done by the spawned subprocess
            error_callback(job)
        except (Exception, BaseException) as ex:
            self.print_job_error(job)
            print_exception(ex, self.workflow.linemaps)
            error_callback(job)

    def handle_job_success(self, job):
        super().handle_job_success(job)

    def handle_job_error(self, job):
        super().handle_job_error(job)
        job.cleanup()
        self.workflow.persistence.cleanup(job)


class ClusterExecutor(RealExecutor):

    default_jobscript = "jobscript.sh"

    def __init__(self, workflow, dag, cores,
                 jobname="spiderjob.{rulename}.{jobid}.sh",
                 printreason=False,
                 quiet=False,
                 printshellcmds=False,
                 latency_wait=3,
                 benchmark_repeats=1,
                 cluster_config=None,
                 local_input=None,
                 restart_times=None,
                 exec_job=None,
                 assume_shared_fs=True):
        local_input = local_input or []
        super().__init__(workflow, dag,
                         printreason=printreason,
                         quiet=quiet,
                         printshellcmds=printshellcmds,
                         latency_wait=latency_wait,
                         benchmark_repeats=benchmark_repeats,
                         assume_shared_fs=assume_shared_fs)

        if not self.assume_shared_fs:
            # use relative path to Spiderfile
            self.spiderfile = os.path.relpath(workflow.spiderfile)

        jobscript = workflow.jobscript
        if jobscript is None:
            jobscript = os.path.join(os.path.dirname(__file__),
                                     self.default_jobscript)
        try:
            with open(jobscript) as f:
                self.jobscript = f.read()
        except IOError as e:
            raise WorkflowError(e)

        if not "jobid" in get_wildcard_names(jobname):
            raise WorkflowError(
                "Defined jobname (\"{}\") has to contain the wildcard {jobid}.")

        if exec_job is None:
            self.exec_job = '\\\n'.join((
                'cd {workflow.workdir_init} && ' if assume_shared_fs else '',
                '{sys.executable} ' if assume_shared_fs else 'python ',
                '-m spider {target} --spiderfile {spiderfile} ',
                '--force -j{cores} --keep-target-files --keep-shadow --keep-remote ',
                '--wait-for-files {wait_for_files} --latency-wait {latency_wait} ',
                '--benchmark-repeats {benchmark_repeats} --attempt {attempt} ',
                '--force-use-threads --wrapper-prefix {workflow.wrapper_prefix} ',
                '{overwrite_workdir} {overwrite_config} {printshellcmds} --nocolor ',
                '--notemp --quiet --no-hooks --nolock'))
        else:
            self.exec_job = exec_job

        if printshellcmds:
            self.exec_job += " --printshellcmds "
        if self.workflow.use_conda:
            self.exec_job += " --use-conda "
            if self.workflow.conda_prefix:
                self.exec_job += " --conda-prefix " + self.workflow.conda_prefix + " "

        self.exec_job += self.get_default_remote_provider_args()

        # force threading.Lock() for cluster jobs
        self.exec_job += " --force-use-threads "

        if not any(dag.dynamic_output_jobs):
            # disable restiction to target rule in case of dynamic rules!
            self.exec_job += " --allowed-rules {job.rule.name} "
        self.jobname = jobname
        self._tmpdir = None
        self.cores = cores if cores else ""
        self.cluster_config = cluster_config if cluster_config else dict()

        self.restart_times = restart_times

        self.active_jobs = list()
        self.lock = threading.Lock()
        self.wait = True
        self.wait_thread = threading.Thread(target=self._wait_for_jobs)
        self.wait_thread.daemon = True
        self.wait_thread.start()

    def shutdown(self):
        with self.lock:
            self.wait = False
        self.wait_thread.join()
        shutil.rmtree(self.tmpdir)

    def cancel(self):
        self.shutdown()

    def _run(self, job, callback=None, error_callback=None):
        if self.assume_shared_fs:
            job.remove_existing_output()
            job.download_remote_input()
        super()._run(job, callback=callback, error_callback=error_callback)
        logger.shellcmd(job.shellcmd)

    @property
    def tmpdir(self):
        if self._tmpdir is None:
            self._tmpdir = mkdtemp(dir=".spider", prefix="tmp.")
        return os.path.abspath(self._tmpdir)

    def get_jobscript(self, job):
        f = job.format_wildcards(self.jobname,
                             rulename=job.rule.name,
                             jobid=self.dag.jobid(job),
                             cluster=self.cluster_wildcards(job))
        if os.path.sep in f:
            raise WorkflowError("Path separator ({}) found in job name {}. "
                                "This is not supported.".format(
                                os.path.sep, f))

        return os.path.join(self.tmpdir, f)

    def format_job(self, pattern, job, **kwargs):
        wait_for_files = []
        if self.assume_shared_fs:
            wait_for_files.append(self.tmpdir)
            wait_for_files.extend(job.local_input)
            wait_for_files.extend(f.local_file()
                                  for f in job.remote_input if not f.stay_on_remote)

            if job.shadow_dir:
                wait_for_files.append(job.shadow_dir)
            if self.workflow.use_conda and job.conda_env:
                wait_for_files.append(job.conda_env)

        format_p = partial(self.format_job_pattern,
                           job=job,
                           properties=json.dumps(job.properties(
                               cluster=self.cluster_params(job))),
                           latency_wait=self.latency_wait,
                           wait_for_files=wait_for_files,
                           **kwargs)
        exec_job = self.exec_job
        try:
            return format_p(pattern)
        except KeyError as e:
            raise WorkflowError(
                "Error formatting jobscript: {} not found\n"
                "Make sure that your custom jobscript is up to date.".format(e))

    def write_jobscript(self, job, jobscript, **kwargs):
        exec_job = self.format_job(self.exec_job,
                                   job,
                                   _quote_all=True,
                                   **kwargs)
        content = self.format_job(self.jobscript,
                                  job,
                                  exec_job=exec_job,
                                  **kwargs)
        with open(jobscript, "w") as f:
            print(content, file=f)
        os.chmod(jobscript, os.stat(jobscript).st_mode | stat.S_IXUSR)

    def cluster_params(self, job):
        """Return wildcards object for job from cluster_config."""

        cluster = self.cluster_config.get("__default__", dict()).copy()
        cluster.update(self.cluster_config.get(job.rule.name, dict()))
        # Format values with available parameters from the job.
        for key, value in list(cluster.items()):
            if isinstance(value, str):
                cluster[key] = job.format_wildcards(value)

        return cluster

    def cluster_wildcards(self, job):
        return Wildcards(fromdict=self.cluster_params(job))

    def handle_job_success(self, job):
        super().handle_job_success(job, upload_remote=False)

    def handle_job_error(self, job):
        # TODO what about removing empty remote dirs?? This cannot be decided
        # on the cluster node.
        super().handle_job_error(job, upload_remote=False)


GenericClusterJob = namedtuple("GenericClusterJob", "job jobid callback error_callback jobscript jobfinished jobfailed")


class GenericClusterExecutor(ClusterExecutor):
    def __init__(self, workflow, dag, cores,
                 submitcmd="qsub",
                 statuscmd=None,
                 cluster_config=None,
                 jobname="spiderjob.{rulename}.{jobid}.sh",
                 printreason=False,
                 quiet=False,
                 printshellcmds=False,
                 latency_wait=3,
                 benchmark_repeats=1,
                 restart_times=0,
                 assume_shared_fs=True):

        self.submitcmd = submitcmd
        if not assume_shared_fs and statuscmd is None:
            raise WorkflowError("When no shared filesystem can be assumed, a "
                "status command must be given.")

        self.statuscmd = statuscmd
        self.external_jobid = dict()

        super().__init__(workflow, dag, cores,
                         jobname=jobname,
                         printreason=printreason,
                         quiet=quiet,
                         printshellcmds=printshellcmds,
                         latency_wait=latency_wait,
                         benchmark_repeats=benchmark_repeats,
                         cluster_config=cluster_config,
                         restart_times=restart_times,
                         assume_shared_fs=assume_shared_fs)

        if assume_shared_fs:
            # TODO wrap with watch and touch {jobrunning}
            # check modification date of {jobrunning} in the wait_for_job method
            self.exec_job += ' && touch "{jobfinished}" || (touch "{jobfailed}"; exit 1)'
        else:
            self.exec_job += ' && exit 0 || exit 1'

    def cancel(self):
        logger.info("Will exit after finishing currently running jobs.")
        self.shutdown()

    def run(self, job,
            callback=None,
            submit_callback=None,
            error_callback=None):
        super()._run(job)
        workdir = os.getcwd()
        jobid = self.dag.jobid(job)

        jobscript = self.get_jobscript(job)
        jobfinished = os.path.join(self.tmpdir, "{}.jobfinished".format(jobid))
        jobfailed = os.path.join(self.tmpdir, "{}.jobfailed".format(jobid))
        self.write_jobscript(job, jobscript,
                             jobfinished=jobfinished,
                             jobfailed=jobfailed)

        deps = " ".join(self.external_jobid[f] for f in job.input
                        if f in self.external_jobid)
        try:
            submitcmd = job.format_wildcards(
                self.submitcmd,
                dependencies=deps,
                cluster=self.cluster_wildcards(job))
        except AttributeError as e:
            raise WorkflowError(str(e), rule=job.rule)
        try:
            ext_jobid = subprocess.check_output(
                '{submitcmd} "{jobscript}"'.format(submitcmd=submitcmd,
                                                   jobscript=jobscript),
                shell=True).decode().split("\n")
        except subprocess.CalledProcessError as ex:
            logger.error("Error submitting jobscript (exit code {}):\n{}".format(
                    ex.returncode, ex.output.decode()))
            error_callback(job)
            return
        if ext_jobid and ext_jobid[0]:
            ext_jobid = ext_jobid[0]
            self.external_jobid.update((f, ext_jobid) for f in job.output)
            logger.info("Submitted job {} with external jobid '{}'.".format(
                jobid, ext_jobid))

        submit_callback(job)
        with self.lock:
            self.active_jobs.append(GenericClusterJob(job, ext_jobid, callback, error_callback, jobscript, jobfinished, jobfailed))

    def _wait_for_jobs(self):
        if self.statuscmd is not None:
            def job_status(job):
                return subprocess.check_output(
                    '{statuscmd} {jobid}'.format(jobid=job.jobid,
                                                 statuscmd=self.statuscmd),
                    shell=True).decode().split("\n")[0]

            def job_finished(job):
                if job_status(job) == "success":
                    return True
                return False

            def job_failed(job):
                if job_status(job) == "failed":
                    return True
                return False
        else:
            def job_finished(job):
                if os.path.exists(active_job.jobfinished):
                    os.remove(active_job.jobfinished)
                    os.remove(active_job.jobscript)
                    return True
                return False

            def job_failed(job):
                if os.path.exists(active_job.jobfailed):
                    os.remove(active_job.jobfailed)
                    os.remove(active_job.jobscript)
                    return True
                return False

        while True:
            with self.lock:
                if not self.wait:
                    return
                active_jobs = self.active_jobs
                self.active_jobs = list()
                for active_job in active_jobs:
                    if job_finished(active_job):
                        active_job.callback(active_job.job)
                    elif job_failed(active_job):
                        self.print_job_error(
                            active_job.job,
                            cluster_jobid=active_job.jobid if active_job.jobid else "unknown",
                        )
                        active_job.error_callback(active_job.job)
                    else:
                        self.active_jobs.append(active_job)
            time.sleep(30)


SynchronousClusterJob = namedtuple("SynchronousClusterJob", "job jobid callback error_callback jobscript process")


class SynchronousClusterExecutor(ClusterExecutor):
    """
    invocations like "qsub -sync y" (SGE) or "bsub -K" (LSF) are
    synchronous, blocking the foreground thread and returning the
    remote exit code at remote exit.
    """

    def __init__(self, workflow, dag, cores,
                 submitcmd="qsub",
                 cluster_config=None,
                 jobname="spiderjob.{rulename}.{jobid}.sh",
                 printreason=False,
                 quiet=False,
                 printshellcmds=False,
                 latency_wait=3,
                 benchmark_repeats=1,
                 restart_times=0,
                 assume_shared_fs=True):
        super().__init__(workflow, dag, cores,
                         jobname=jobname,
                         printreason=printreason,
                         quiet=quiet,
                         printshellcmds=printshellcmds,
                         latency_wait=latency_wait,
                         benchmark_repeats=benchmark_repeats,
                         cluster_config=cluster_config,
                         restart_times=restart_times,
                         assume_shared_fs=assume_shared_fs)
        self.submitcmd = submitcmd
        self.external_jobid = dict()

    def cancel(self):
        logger.info("Will exit after finishing currently running jobs.")
        self.shutdown()

    def run(self, job,
            callback=None,
            submit_callback=None,
            error_callback=None):
        super()._run(job)
        workdir = os.getcwd()
        jobid = self.dag.jobid(job)

        jobscript = self.get_jobscript(job)
        self.write_jobscript(job, jobscript)

        deps = " ".join(self.external_jobid[f] for f in job.input
                        if f in self.external_jobid)
        try:
            submitcmd = job.format_wildcards(
                self.submitcmd,
                dependencies=deps,
                cluster=self.cluster_wildcards(job))
        except AttributeError as e:
            raise WorkflowError(str(e), rule=job.rule)

        process = subprocess.Popen('{submitcmd} "{jobscript}"'.format(submitcmd=submitcmd,
                                           jobscript=jobscript), shell=True)
        submit_callback(job)

        with self.lock:
            self.active_jobs.append(SynchronousClusterJob(job, process.pid, callback, error_callback, jobscript, process))

    def _wait_for_jobs(self):
        while True:
            with self.lock:
                if not self.wait:
                    return
                active_jobs = self.active_jobs
                self.active_jobs = list()
                for active_job in active_jobs:
                    exitcode = active_job.process.poll()
                    if exitcode is None:
                        # job not yet finished
                        self.active_jobs.append(active_job)
                    elif exitcode == 0:
                        # job finished successfully
                        os.remove(active_job.jobscript)
                        active_job.callback(active_job.job)
                    else:
                        # job failed
                        os.remove(active_job.jobscript)
                        self.print_job_error(active_job.job)
                        print_exception(ClusterJobException(active_job, self.dag.jobid(active_job.job)),
                                        self.workflow.linemaps)
                        active_job.error_callback(active_job.job)
            time.sleep(1)


DRMAAClusterJob = namedtuple("DRMAAClusterJob", "job jobid callback error_callback jobscript")


class DRMAAExecutor(ClusterExecutor):
    def __init__(self, workflow, dag, cores,
                 jobname="spiderjob.{rulename}.{jobid}.sh",
                 printreason=False,
                 quiet=False,
                 printshellcmds=False,
                 drmaa_args="",
                 drmaa_log_dir=None,
                 latency_wait=3,
                 benchmark_repeats=1,
                 cluster_config=None,
                 restart_times=0,
                 assume_shared_fs=True):
        super().__init__(workflow, dag, cores,
                         jobname=jobname,
                         printreason=printreason,
                         quiet=quiet,
                         printshellcmds=printshellcmds,
                         latency_wait=latency_wait,
                         benchmark_repeats=benchmark_repeats,
                         cluster_config=cluster_config,
                         restart_times=restart_times,
                         assume_shared_fs=assume_shared_fs)
        try:
            import drmaa
        except ImportError:
            raise WorkflowError(
                "Python support for DRMAA is not installed. "
                "Please install it, e.g. with easy_install3 --user drmaa")
        except RuntimeError as e:
            raise WorkflowError("Error loading drmaa support:\n{}".format(e))
        self.session = drmaa.Session()
        self.drmaa_args = drmaa_args
        self.drmaa_log_dir = drmaa_log_dir
        self.session.initialize()
        self.submitted = list()

    def cancel(self):
        from drmaa.const import JobControlAction
        from drmaa.errors import InvalidJobException, InternalException
        for jobid in self.submitted:
            try:
                self.session.control(jobid, JobControlAction.TERMINATE)
            except (InvalidJobException, InternalException):
                #This is common - logging a warning would probably confuse the user.
                pass
        self.shutdown()

    def run(self, job,
            callback=None,
            submit_callback=None,
            error_callback=None):
        super()._run(job)
        jobscript = self.get_jobscript(job)
        self.write_jobscript(job, jobscript)

        try:
            drmaa_args = job.format_wildcards(
                self.drmaa_args,
                cluster=self.cluster_wildcards(job))
        except AttributeError as e:
            raise WorkflowError(str(e), rule=job.rule)

        import drmaa

        if self.drmaa_log_dir:
            makedirs(self.drmaa_log_dir)

        try:
            jt = self.session.createJobTemplate()
            jt.remoteCommand = jobscript
            jt.nativeSpecification = drmaa_args
            if self.drmaa_log_dir:
                jt.outputPath = ":" + self.drmaa_log_dir
                jt.errorPath = ":" + self.drmaa_log_dir
            jt.jobName = os.path.basename(jobscript)

            jobid = self.session.runJob(jt)
        except (drmaa.InternalException,
                drmaa.InvalidAttributeValueException) as e:
            print_exception(WorkflowError("DRMAA Error: {}".format(e)),
                            self.workflow.linemaps)
            error_callback(job)
            return
        logger.info("Submitted DRMAA job {} with external jobid {}.".format(self.dag.jobid(job), jobid))
        self.submitted.append(jobid)
        self.session.deleteJobTemplate(jt)

        submit_callback(job)

        with self.lock:
            self.active_jobs.append(DRMAAClusterJob(job, jobid, callback, error_callback, jobscript))

    def shutdown(self):
        super().shutdown()
        self.session.exit()

    def _wait_for_jobs(self):
        import drmaa
        while True:
            with self.lock:
                if not self.wait:
                    return
                active_jobs = self.active_jobs
                self.active_jobs = list()
                for active_job in active_jobs:
                    try:
                        retval = self.session.wait(active_job.jobid,
                                                   drmaa.Session.TIMEOUT_NO_WAIT)
                    except drmaa.ExitTimeoutException as e:
                        # job still active
                        self.active_jobs.append(active_job)
                        continue
                    except (drmaa.InternalException, Exception) as e:
                        print_exception(WorkflowError("DRMAA Error: {}".format(e)),
                                        self.workflow.linemaps)
                        os.remove(active_job.jobscript)
                        active_job.error_callback(active_job.job)
                        continue
                    # job exited
                    os.remove(active_job.jobscript)
                    if retval.hasExited and retval.exitStatus == 0:
                        active_job.callback(active_job.job)
                    else:
                        self.print_job_error(active_job.job)
                        print_exception(
                            ClusterJobException(active_job, self.dag.jobid(active_job.job)),
                            self.workflow.linemaps)
                        active_job.error_callback(active_job.job)
            time.sleep(1)


@contextlib.contextmanager
def change_working_directory(directory=None):
    """ Change working directory in execution context if provided. """
    if directory:
        try:
            saved_directory = os.getcwd()
            logger.info("Changing to shadow directory: {}".format(directory))
            os.chdir(directory)
            yield
        finally:
            os.chdir(saved_directory)
    else:
        yield


KubernetesJob = namedtuple("KubernetesJob", "job jobid callback error_callback kubejob jobscript")


class KubernetesExecutor(ClusterExecutor):
    def __init__(self, workflow, dag, namespace, envvars,
                 jobname="{rulename}.{jobid}",
                 printreason=False,
                 quiet=False,
                 printshellcmds=False,
                 latency_wait=3,
                 benchmark_repeats=1,
                 cluster_config=None,
                 local_input=None,
                 restart_times=None):

        exec_job = (
            'spider {target} --spiderfile {spiderfile} '
            '--force -j{cores} --keep-target-files --keep-shadow --keep-remote '
            '--latency-wait 0 '
            '--benchmark-repeats {benchmark_repeats} --attempt {attempt} '
            '--force-use-threads --wrapper-prefix {workflow.wrapper_prefix} '
            '{overwrite_config} {printshellcmds} --nocolor '
            '--notemp --quiet --no-hooks --nolock ')

        super().__init__(workflow, dag, None,
                         jobname=jobname,
                         printreason=printreason,
                         quiet=quiet,
                         printshellcmds=printshellcmds,
                         latency_wait=latency_wait,
                         benchmark_repeats=benchmark_repeats,
                         cluster_config=cluster_config,
                         local_input=local_input,
                         restart_times=restart_times,
                         exec_job=exec_job,
                         assume_shared_fs=False)
        # use relative path to Spiderfile
        self.spiderfile = os.path.relpath(workflow.spiderfile)

        from kubernetes import config
        config.load_kube_config()

        import kubernetes.client
        self.kubeapi = kubernetes.client.CoreV1Api()
        self.batchapi = kubernetes.client.BatchV1Api()
        self.namespace = namespace
        self.envvars = envvars
        self.secret_files = {}
        self.run_namespace = str(uuid.uuid4())
        self.secret_envvars = {}
        self.register_secret()

    def register_secret(self):
        import kubernetes.client

        secret = kubernetes.client.V1Secret()
        secret.metadata = kubernetes.client.V1ObjectMeta()
        # create a random uuid
        secret.metadata.name = self.run_namespace
        secret.type = "Opaque"
        secret.data = {}
        for i, f in enumerate(self.workflow.get_sources()):
            if f.startswith(".."):
                logger.warning("Ignoring source file {}. Only files relative "
                               "to the working directory are allowed.")
                continue
            with open(f, "br") as content:
                key = "f{}".format(i)
                self.secret_files[key] = f
                secret.data[key] = base64.b64encode(content.read()).decode()
        for e in self.envvars:
            try:
                key = e.lower()
                secret.data[key] = base64.b64encode(os.environ[e].encode()).decode()
                self.secret_envvars[key] = e
            except KeyError:
                continue
        self.kubeapi.create_namespaced_secret(self.namespace, secret)

    def shutdown(self):
        super().shutdown()

    def cancel(self):
        import kubernetes.client
        body = kubernetes.client.V1DeleteOptions()
        with self.lock:
            for j in self.active_jobs:
                self.kubeapi.delete_namespaced_pod(
                    j.jobid, self.namespace, body)
        self.shutdown()

    def run(self, job,
            callback=None,
            submit_callback=None,
            error_callback=None):
        import kubernetes.client

        super()._run(job)
        exec_job = self.format_job(self.exec_job, job, _quote_all=True)
        jobid = "spiderjob-{}-{}".format(self.run_namespace, self.dag.jobid(job))

        body = kubernetes.client.V1Pod()
        body.metadata = kubernetes.client.V1ObjectMeta()
        body.metadata.name = jobid

        body.spec = kubernetes.client.V1PodSpec()
        # fail on first error
        body.spec.restart_policy = "Never"

        # container
        container = kubernetes.client.V1Container()
        container.image = "quay.io/spider/spider:{}".format(__version__)
        container.command = shlex.split(exec_job)
        container.name = jobid
        container.working_dir = "/workdir"
        container.volume_mounts = [kubernetes.client.V1VolumeMount(
            name="workdir", mount_path="/workdir")]
        body.spec.containers = [container]

        # source files
        secret_volume = kubernetes.client.V1Volume()
        secret_volume.name = "workdir"
        secret_volume.secret = kubernetes.client.V1SecretVolumeSource()
        secret_volume.secret.secret_name = self.run_namespace
        secret_volume.secret.items = [
            kubernetes.client.V1KeyToPath(key=key, path=path)
            for key, path in self.secret_files.items()
        ]
        body.spec.volumes = [secret_volume]

        # env vars
        container.env = []
        for key, e in self.secret_envvars.items():
            envvar = kubernetes.client.V1EnvVar(name=e)
            envvar.value_from = kubernetes.client.V1EnvVarSource()
            envvar.value_from.secret_key_ref = kubernetes.client.V1SecretKeySelector(
                key=key, name=self.run_namespace)
            container.env.append(envvar)

        # request resources
        container.resources = kubernetes.client.V1ResourceRequirements()
        container.resources.requests = {}
        # Subtract 1 from the requested number of cores.
        # The reason is that kubernetes requires some cycles for
        # maintenance, but won't use a full core for that.
        # This way, we should be able to saturate the node without exceeding it
        # too much.
        container.resources.requests["cpu"] = job.resources["_cores"] - 1
        if "mem_mb" in job.resources:
            container.resources.requests["memory"] = "{}M".format(
                job.resources["mem_mb"])

        pod = self.kubeapi.create_namespaced_pod(self.namespace, body)
        logger.info("Get status with:\n"
                    "kubectl describe pod {jobid}\n"
                    "kubectl logs {jobid}".format(jobid=jobid))
        self.active_jobs.append(KubernetesJob(
            job, jobid, callback, error_callback, pod, None))

    def _wait_for_jobs(self):
        while True:
            with self.lock:
                if not self.wait:
                    return
                active_jobs = self.active_jobs
                self.active_jobs = list()
                for j in active_jobs:
                    res = self.kubeapi.read_namespaced_pod_status(
                        j.jobid, self.namespace)
                    if res.status.phase == "Failed":
                        msg = ("For details, please issue:\n"
                               "kubectl describe pod {jobid}\n"
                               "kubectl logs {jobid}").format(jobid=j.jobid)
                        # failed
                        self.print_job_error(j.job, msg=msg, jobid=j.jobid)
                        j.error_callback(j.job)
                    elif res.status.phase == "Succeeded":
                        # finished
                        j.callback(j.job)
                    else:
                        # still active
                        self.active_jobs.append(j)
            time.sleep(1)


def run_wrapper(job_rule, input, output, params, wildcards, threads, resources, log,
                benchmark, benchmark_repeats, conda_env, linemaps, debug=False,
                shadow_dir=None):
    """
    Wrapper around the run method that handles exceptions and benchmarking.

    Arguments
    job_rule   -- the ``job.rule`` member
    input      -- list of input files
    output     -- list of output files
    wildcards  -- so far processed wildcards
    threads    -- usable threads
    log        -- list of log files
    shadow_dir -- optional shadow directory root
    """
    # get shortcuts to job_rule members
    run = job_rule.run_func
    version = job_rule.version
    rule = job_rule.name

    if os.name == "posix" and debug:
        sys.stdin = open('/dev/stdin')

    if benchmark is not None:
        from spider.benchmark import BenchmarkRecord, benchmarked, write_benchmark_records

    try:
        with change_working_directory(shadow_dir):
            if benchmark:
                bench_records = []
                for i in range(benchmark_repeats):
                    # Determine whether to benchmark this process or do not
                    # benchmarking at all.  We benchmark this process unless the
                    # execution is done through the ``shell:``, ``script:``, or
                    # ``wrapper:`` stanza.
                    is_sub = job_rule.shellcmd or job_rule.script or job_rule.wrapper
                    if is_sub:
                        # The benchmarking through ``benchmarked()`` is started
                        # in the execution of the shell fragment, script, wrapper
                        # etc, as the child PID is available there.
                        bench_record = BenchmarkRecord()
                        run(input, output, params, wildcards, threads, resources,
                            log, version, rule, conda_env, bench_record)
                    else:
                        # The benchmarking is started here as we have a run section
                        # and the generated Python function is executed in this
                        # process' thread.
                        with benchmarked() as bench_record:
                            run(input, output, params, wildcards, threads, resources,
                                log, version, rule, conda_env, bench_record)
                    # Store benchmark record for this iteration
                    bench_records.append(bench_record)
            else:
                run(input, output, params, wildcards, threads, resources,
                    log, version, rule, conda_env, None)
    except (KeyboardInterrupt, SystemExit) as e:
        # Re-raise the keyboard interrupt in order to record an error in the
        # scheduler but ignore it
        raise e
    except (Exception, BaseException) as ex:
        log_verbose_traceback(ex)
        # this ensures that exception can be re-raised in the parent thread
        lineno, file = get_exception_origin(ex, linemaps)
        raise RuleException(format_error(ex, lineno,
                                         linemaps=linemaps,
                                         spiderfile=file,
                                         show_traceback=True))

    if benchmark is not None:
        try:
            write_benchmark_records(bench_records, benchmark)
        except (Exception, BaseException) as ex:
            raise WorkflowError(ex)
