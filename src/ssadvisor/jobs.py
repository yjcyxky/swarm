# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

from __future__ import absolute_import, unicode_literals
import logging
import os
import time
import jinja2
from configparser import ConfigParser
from configparser import NoSectionError
from jinja2 import TemplateSyntaxError
from jinja2 import TemplateAssertionError

try:
    from ssadvisor import drmaa_api as drmaa
except ImportError:
    import drmaa

class JobTemplateError(Exception):
    pass

class JobDirError(Exception):
    pass

class JobTemplateNotFound(Exception):
    pass

class JobParameterError(Exception):
    pass

class JobVarsConfigError(Exception):
    pass

def render_template(tpl_path, context):
    path, filename = os.path.split(tpl_path)
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(path or './')
    ).get_template(filename).render(context)

class Config:
    def __init__(self, config_path):
        self._config_path = config_path
        self._cf = ConfigParser()
        self._cf.read(self._config_path)

    def get_section(self, section_name):
        try:
            return self._cf.items(section_name)
        except NoSectionError:
            raise JobVarsConfigError("The Config file %s doesn't contain %s section" % (self._config_path, section_name))

class Job:
    def __init__(self, jobname = None, jobid = None, bash_templ_path = None,
                 vars_file_path = None, output_dir='/tmp/jobs',
                 log_dir = '/tmp/jobs/logs', status_code_flag = False):
        self._logger = logging.getLogger(__name__)
        self._output_dir = output_dir
        self._logs_path = log_dir if log_dir else os.path.join(self._output_dir, 'logs')
        self._job_template = None
        self._jobname = jobname    # JobName must be same with the section name of vars_file
        self._jobid = None    # For getting status or controlling job when jobid is not None
        self._jobstatus = None
        self._vars = None
        self._status_code_flag = status_code_flag

        if jobid is not None:
            self._jobid = jobid
        # If jobid is None, You must specify jobname, bash_templ_path, vars_file_path variables.
        elif not (vars_file_path and bash_templ_path and jobname and output_dir):
            self._logger.error('You must specify bash_templ_path, vars_file_path,'
                               'and jobname parameters when jobid is None..')
            raise JobParameterError('You must specify bash_templ_path, vars_file_path,'
                                    'and jobname parameters when jobid is None.')
        else:
            if jobname is not None:
                self._jobname = jobname

            if vars_file_path is not None:
                config = Config(vars_file_path)
                self._vars = config.get_section(jobname)

            if output_dir is not None:
                if not os.path.isdir(self._output_dir):
                    self._mkdir_p(self._output_dir)
                if not os.path.isdir(self._logs_path):
                    self._setup_logs(self._logs_path)

            if bash_templ_path is not None:
                if os.path.isfile(bash_templ_path):
                    try:
                        if self._vars is not None:
                            self._job_template = render_template(bash_templ_path, self._vars)
                        else:
                            self._job_template = render_template(bash_templ_path, {})
                        job_file_path = os.path.join(output_dir, '%s.job' % self._jobname)
                        with open(job_file_path, 'w') as f:
                            f.write(self._job_template)
                        os.chmod(job_file_path, 0o700)
                    except (TemplateSyntaxError, TemplateAssertionError) as e:
                        self._logger.error('Exist a problem with the template: %s' % str(e))
                        raise JobTemplateError('Template Error.')
                else:
                    raise JobTemplateNotFound('No Such File %s' % bash_templ_path)

    def _mkdir_p(self, path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                self._logger.error("Can't create %s directory." % output_dir)
                raise JobDirError('Create Job Directory %s Error.' % output_dir)

    def _setup_logs(self, logs_path):
        self._mkdir_p(logs_path)

    def get_job_template(self):
        return self._job_template

    def get_jobid(self):
        return self._jobid

    def _get_path(self, path):
        return ":" + path

    def _check_file(self, path):
        if not os.path.isfile(path):
            os.mknod(path)

    def _gen_path(self, jobname):
        # current_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
        error_path = os.path.join(self._logs_path, '%s-err.log' % jobname)
        self._check_file(error_path)
        output_path = os.path.join(self._logs_path, '%s-out.log' % jobname)
        self._check_file(output_path)
        return output_path, error_path

    def submit_job(self):
        if (self._jobname and self._output_dir and self._logs_path):
            with drmaa.Session() as s:
                self._logger.info('Creating job template')
                jt = s.createJobTemplate()
                jt.remoteCommand = os.path.join(self._output_dir, '%s.job' % self._jobname)
                jt.joinFiles = True
                jt.workingDirectory = self._output_dir
                output_path, error_path = self._gen_path(self._jobname)
                jt.errorPath = self._get_path(error_path)
                jt.outputPath = self._get_path(output_path)
                jt.jobName = self._jobname
                self._jobid = s.runJob(jt)
                self._logger.info('Your job has been submitted with ID %s' % self._jobid)
                self._logger.info('Cleaning up')
                s.deleteJobTemplate(jt)

    def get_jobstatus(self):
        if self._jobid is None:
            self._logger.debug('You must call submit_job method firstly.')
        else:
            # Who needs a case statement when you have dictionaries?
            decodestatus = {
                drmaa.JobState.UNDETERMINED: 'process status cannot be determined',
                drmaa.JobState.QUEUED_ACTIVE: 'job is queued and active',
                drmaa.JobState.SYSTEM_ON_HOLD: 'job is queued and in system hold',
                drmaa.JobState.USER_ON_HOLD: 'job is queued and in user hold',
                drmaa.JobState.USER_SYSTEM_ON_HOLD: 'job is queued and in user and system hold',
                drmaa.JobState.RUNNING: 'job is running',
                drmaa.JobState.SYSTEM_SUSPENDED: 'job is system suspended',
                drmaa.JobState.USER_SUSPENDED: 'job is user suspended',
                drmaa.JobState.DONE: 'job finished normally',
                drmaa.JobState.FAILED: 'job finished, but failed'
            }
            with drmaa.Session() as s:
                self._logger.debug('Checking %s status.' % self._jobid)
                if self._status_code_flag:
                    self._jobstatus = s.jobStatus(self._jobid)
                else:
                    self._jobstatus = decodestatus.get(s.jobStatus(self._jobid))
                self._logger.info('JobStatus: %s' % self._jobstatus)

            return self._jobstatus

    def terminate_job(self):
        if self._jobid is None:
            self._logger.debug('You must call submit_job method firstly.')
        else:
            with drmaa.Session() as s:
                self._logger.debug('Terminating %s.' % self._jobid)
                s.control(self._jobid, drmaa.JobControlAction.TERMINATE)
                self._logger.info('%s is terminated.' % self._jobid)
                if self._status_code_flag:
                    self._jobstatus = drmaa.JobState.FAILED
                else:
                    self._jobstatus = 'job is terminated by user'
            return self._jobstatus


def test():
    bash_templ_path = '/tmp/get_hostname'
    vars_file_path = '/tmp/vars'
    jobname = 'test'
    job = Job(jobname, bash_templ_path = bash_templ_path, vars_file_path = vars_file_path)
    print(job.get_job_template())
    job.submit_job()
    print(job.get_jobid())
    print(job.get_jobstatus())
    # print(job.terminate_job())

def test_config():
    cf = Config('vars')
    print(cf.get_section('test'))

if __name__ == '__main__':
    test()
    # test_config()
