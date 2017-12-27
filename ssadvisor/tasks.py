from __future__ import absolute_import, unicode_literals
from celery import shared_task, states
from celery.utils.log import get_task_logger
from celery.exceptions import Ignore

logger = get_task_logger(__name__)

@shared_task(bind = True)
def submit_job(self, task_uuid):
    import uuid
    import os
    import json
    from jobs import Job
    from ssadvisor.models import TaskPool, Task

    try:
        task = Task.objects.get(task_uuid = task_uuid)
        package = task.package
        # Package安装目录下的templates目录中必须包含一个bash_template.sh文件
        bash_templ_path = os.path.join(cobweb_home,
                                       '%s-%s' % (package.name, package.version),
                                       'templates', 'bash_template.sh')
        # job_vars_file由前端变量渲染生成，frontend_templ指定前端需要生成哪些变量
        # job_vars_file文件包含一个字典：以`task_name`为键，其它变量为键值对的字典
        vars_file_path = task.config_path
        output_dir = task.output_path
        log_dir = task.log_path
        jobname = task.task_name

        job = Job(jobname = jobname, bash_templ_path = bash_templ_path,
                  vars_file_path = vars_file_path, output_dir = output_dir,
                  log_dir = log_dir)
        job.submit_job()
        logger.info('Your job has been submitted with ID %s' % job.get_jobid())

        jobid = job.get_jobid()
        with open(package.output_templ, 'r') as f:
            output_templ = json.load(f)
            result_files = output_templ.get('result_files')
            result_files_text = json.dumps(result_files)

        taskpool = TaskPool.objects.create(task_pool_uuid = uuid.uuid4(),
                                           task = task, jobid = jobid,
                                           result_file_flags = result_files_text)
        taskpool.save()
        # 置位flag：Submitted Job
        task.progress_percentage = 0
        task.save()
    except:
        logger.error(str(sys.exc_info()))
        # manually update the task state
        self.update_state(
            state = states.FAILURE,
            meta = str(sys.exc_info())
        )

        # ignore the task so no other state is recorded
        raise Ignore()

@shared_task(bind=True)
def update_jobstatus(self, jobid = None, task_uuid = None):
    # TODO: How to update jobstatus? job status code or return code?
    # TODO: How to update progress_percentage?    Check file status?
    import uuid
    import os
    import sys
    import time
    from jobs import Job
    from ssadvisor.models import TaskPool

    try:
        try:
            if jobid:
                running_task = TaskPool.objects.get(jobid = jobid)
            else:
                running_task = TaskPool.objects.get(task_id = task_uuid)
        except TaskPool.DoesNotExist:
            # manually update the task state
            self.update_state(
                state = states.FAILURE,
                meta = 'No Such Job ID(%s) or Task UUID(%s).' % (jobid, task_uuid)
            )

            # ignore the task so no other state is recorded
            raise Ignore()

        task = running_task.task

        # Fetch Job Status
        job = Job(jobid = jobid)
        jobstatus = job.get_jobstatus()

        # Update a record in database
        running_task.jobstatus = jobstatus
        updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        running_task.updated_time = updated_time
        running_task.save()

        task = running_task.task
        output_path = task.output_path
        if jobstatus == 'running':
            # 获取结果文件列表计算percentage
            result_file_flags = json.loads(running_task.result_file_flags)
            percentage = 0
            step = 100 / len(result_file_flags)
            for result_file in result_file_flags:
                if check_file(os.path.join(output_path, result_file)):
                    percentage = percentage + step

            task.progress_percentage = percentage
        elif jobstatus == 'queued_active':
            task.progress_percentage = 0
        elif jobstatus == 'done':
            task.progress_percentage = 100
            task.finished_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            running_task.delete()
        elif jobstatus == 'failed':
            log_path = task.log_path
            task_name = task.task_name
            task.finished_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            # The name of job log file must be same with submit_job method
            with open(os.path.join(log_path, '%s-err.log' % task_name)) as f:
                log_string = json.load(f)
                task.msg = log_string
            running_task.delete()
        # 保存job运行状态
        task.jobstatus = jobstatus
        task.save()
    except:
        logger.error(str(sys.exc_info()))
        # manually update the task state
        self.update_state(
            state = states.FAILURE,
            meta = str(sys.exc_info())
        )

        # ignore the task so no other state is recorded
        raise Ignore()

@shared_task(bind = True)
def terminate_job(self, jobid):
    import uuid
    import os
    import sys
    from jobs import Job
    from ssadvisor.models import TaskPool

    try:
        try:
            taskpool = TaskPool.objects.get(jobid = jobid)
        except TaskPool.DoesNotExist:
            # TODO:
            pass

        task = taskpool.task

        job = Job(jobid = jobid)
        jobstatus = job.terminate_job()
        task.finished_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        task.msg = jobstatus
        task.jobstatus = 'failed'
        task.save()
    except:
        logger.error(str(sys.exc_info()))
        # manually update the task state
        self.update_state(
            state = states.FAILURE,
            meta = str(sys.exc_info())
        )

        # ignore the task so no other state is recorded
        raise Ignore()

@shared_task(bind = True)
def loop_submit_job(self):
    from jobs import Job
    from ssadvisor.models import (TaskPool, Task, Setting)
    from ssadvisor.utils import get_settings
    from django.db.models import Q
    import uuid
    import os
    import sys
    import json

    taskpool_count = TaskPool.objects.count()
    advisor_setting = get_settings(Setting)
    max_task_num = advisor_setting.max_task_num
    if taskpool_count < max_task_num:
        try:
            tasks = Task.objects.filter(Q(progress_percentage = -1)) \
                                .order_by('priority_level', 'created_time')
            tasks = tasks[0:(max_task_num - taskpool_count)]
            for task in tasks:
                package = task.package
                # Package安装目录下的templates目录中必须包含一个bash_template.sh文件
                bash_templ_path = os.path.join(cobweb_home,
                                               '%s-%s' % (package.name, package.version),
                                               'templates', 'bash_template.sh')
                # job_vars_file由前端变量渲染生成，frontend_templ指定前端需要生成哪些变量
                # job_vars_file文件包含一个字典：以`task_name`为键，其它变量为键值对的字典
                vars_file_path = task.config_path
                output_dir = task.output_path
                log_dir = task.log_path
                jobname = task.task_name

                job = Job(jobname = jobname, bash_templ_path = bash_templ_path,
                          vars_file_path = vars_file_path, output_dir = output_dir,
                          log_dir = log_dir)
                job.submit_job()
                logger.info('Your job has been submitted with ID %s' % job.get_jobid())

                jobid = job.get_jobid()
                with open(package.output_templ, 'r') as f:
                    output_templ = json.load(f)
                    result_files = output_templ.get('result_files')
                    result_files_text = json.dumps(result_files)

                taskpool = TaskPool.objects.create(task_pool_uuid = uuid.uuid4(),
                                                   task = task, jobid = jobid,
                                                   result_file_flags = result_files_text)
                taskpool.save()
                # 置位flag：Submitted Job
                task.progress_percentage = 0
                task.save()
        except:
            logger.error(str(sys.exc_info()))
            # manually update the task state
            self.update_state(
                state = states.FAILURE,
                meta = str(sys.exc_info())
            )

            # ignore the task so no other state is recorded
            raise Ignore()
    else:
        logger.info('Reached the maximum number of tasks limit.')


@shared_task(bind = True)
def loop_update_status(self):
    from jobs import Job
    from ssadvisor.models import TaskPool
    import time
    import sys
    import os
    import json

    def check_file(path):
        if os.path.isfile(path):
            return True
        else:
            return False

    running_tasks = TaskPool.objects.all()

    for running_task in running_tasks:
        try:
            jobid = running_task.jobid
            logger.info('Update job status for %s' % jobid)
            job = Job(jobid = jobid, status_code_flag = True)
            jobstatus = job.get_jobstatus()
            logger.info('Job status: %s' % jobstatus)

            running_task.jobstatus = jobstatus
            running_task.updated_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            running_task.save()

            task = running_task.task
            output_path = task.output_path

            if jobstatus == 'running':
                # 获取结果文件列表计算percentage
                result_file_flags = json.loads(running_task.result_file_flags)
                percentage = 0
                step = 100 / len(result_file_flags)
                for result_file in result_file_flags:
                    if check_file(os.path.join(output_path, result_file)):
                        percentage = percentage + step

                task.progress_percentage = percentage
            elif jobstatus == 'queued_active':
                task.progress_percentage = 0
            elif jobstatus == 'done':
                task.progress_percentage = 100
                task.finished_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                running_task.delete()
            elif jobstatus == 'failed':
                log_path = task.log_path
                task_name = task.task_name
                task.finished_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                # The name of job log file must be same with submit_job method
                with open(os.path.join(log_path, '%s-err.log' % task_name)) as f:
                    log_string = json.load(f)
                    task.msg = log_string
                running_task.delete()
            # 保存job运行状态
            task.jobstatus = jobstatus
            task.save()
        except:
            logger.error(str(sys.exc_info()))
            # manually update the task state
            self.update_state(
                state = states.FAILURE,
                meta = str(sys.exc_info())
            )

            # ignore the task so no other state is recorded
            raise Ignore()
