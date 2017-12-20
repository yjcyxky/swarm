import json, requests, datetime, mongoengine
from cobweb.models.utils import get_items_by_page, render_template, tasks_info_j2_file
from cobweb.models.packages import LinuxPackage, ClusterPackage
from mongoengine.queryset import DoesNotExist
from requests.exceptions import ConnectionError
from cobweb.configuration import config as cobweb_config
from cobweb.utils import filter_task_kwargs

class TaskDoesNotExist(Exception):
    def __init__(self, response):
        self.response = response

class TaskAlreadyExist(Exception):
    def __init__(self, response):
        self.response = response


class CeleryTask:
    '''
    CeleryTask: 任务调度器
    '''
    def __init__(self, task_name, task_action, log_file_path, task_templ = None,
                 task_summary = None):
        # 支持的task_action与tasks包中定义的task一致
        # tasks-package模块定义了如下task：cobweb.install_package,
        #                               cobweb.remove_package,
        #                               cobweb.reinstall_package
        self.task_action = task_action    # 此处task_action等同于Flower中的task_name
        self.task_name = task_name
        self.log_file_path = log_file_path
        self.task_templ = task_templ
        self.task_summary = task_summary
        self.task_id = Task.get_task_id(task_name = task_name)
        self.celery_settings = cobweb_config.get("CELERY_SETTINGS")
        self.flower_api = self.celery_settings.get("flower_api")
        if not (self.celery_settings and self.flower_api):
            app.logger.error("配置文件错误: 缺少CELERY_SETTINGS.")

    def _assert_exist_task(self):
        if self.task_id is None:
            raise TaskDoesNotExist({
                      'message': "Task %s doesn't exist." % self.task_name
                  })

    def _assert_no_task(self):
        if self.task_id:
            raise TaskAlreadyExist({
                      'message': "Task %s already exist." % self.task_name
                  })

    def get_status(self):
        # TODO: 增加错误检测代码
        try:
            self._assert_exist_task()
            task_api = "%s/task/info/%s" % (self.flower_api, self.task_id)
            try:
                resp = requests.get(task_api)
                app.logger.debug("response: %s, %s" % (str(resp), resp.text))
            except ConnectionError as e:
                app.logger.error("Connect to flower error: %s" % str(e))
                err_response = {
                    'message': "Failed to connect to flower."
                }
                return True, "FAILURE", err_response
            if resp.status_code == 404:
                err_response = {
                    'message': "Failed to create task %s." % self.task_name
                }
                return True, "FAILURE", err_response
            elif resp.status_code == 200:
                task_info = resp.json()
                return task_info
        except TaskDoesNotExist as e:
            app.logger.error("Task %s doesn't exist." % self.task_name)
            return True, "FAILURE", e.response

    def add_task(self, *task_args, **task_kwargs):
        if not Task.check_task_ref(task_kwargs):
            err_response = {
                'message': "Can't find task reference. \
task_args:{0}, task_kwargs:{1}".format(str(task_args), str(task_kwargs))
            }
            return True, "FAILURE", err_response
        try:
            self._assert_no_task()
            task_api = "%s/task/async-apply/%s" % (self.flower_api, self.task_action)
            app.logger.debug("task_api: %s" % task_api)
            app.logger.debug("task_kwargs: %s" % str(task_kwargs))

            try:
                post_args = {
                    'args': task_args,
                    'kwargs': task_kwargs
                }
                resp = requests.post(task_api, data = json.dumps(post_args))
                app.logger.info("response: %s" % str(resp))
            except ConnectionError as e:
                app.logger.error("Connect to flower error: %s" % str(e))
                err_response = {
                    'message': "Failed to connect to flower."
                }
                return True, "FAILURE", err_response

            if resp.status_code == 404:
                app.logger.error("Failed to create task %s." % self.task_name)
                err_response = {
                    'message': "Failed to create task %s." % self.task_name
                }
                return True, "FAILURE", err_response
            elif resp.status_code == 200:
                resp = resp.json()
                app.logger.info("Create a task: %s(%s)" % (self.task_name, str(resp)))
                self.task_id = resp.get("task-id")
                task_db_id = Task.add_task(self.task_name, task_kwargs,
                                           self.task_id, self.task_action,
                                           self.log_file_path,
                                           task_templ = self.task_templ,
                                           task_summary = self.task_summary)
                if self.task_id and task_db_id:
                    success_response = {
                        'task_id': str(self.task_id),
                        'task_db_id': str(task_db_id)
                    }
                    return False, "SUCCESS", success_response
                else:
                    err_response = {
                        'message': "Failed to create task %s." % self.task_name
                    }
                    return True, "FAILURE", err_response
            else:
                return True, "FAILURE", {'message': "Unknown error."}
        except TaskAlreadyExist as e:
            app.logger.error("Task %s already exist." % self.task_name)
            return True, "FAILURE", e.response

    def get_result(self):
        result_api = "%s/task/result/%s" % (self.flower_api, self.task_id)
        result_info = requests.get(result_api).json()
        if result_info and result_info.get("state") == "SUCCESS":
            return False, "SUCCESS", result_info.get("result")
        else:
            return True, "FAILURE", None

    def revoke_task(self):
        pass
