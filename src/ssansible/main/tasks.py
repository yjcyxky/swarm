# pylint: disable=broad-except,no-member,redefined-outer-name
import logging
from ssansible.main.utils import prepare_environment
from ssansible.main.utils import task, BaseTask
from ssansible.main.exceptions import TaskError
from ssansible.main.models.utils import AnsibleModule, AnsiblePlaybook
from ssansible.main.models.hooks import Hook

logger = logging.getLogger("ssansible")


def get_app(**kwargs):
    from celery import Celery
    prepare_environment(**kwargs)
    celery_app = Celery('ssansible')
    celery_app.config_from_object('django.conf:settings', namespace='CELERY')
    celery_app.autodiscover_tasks()
    return celery_app


app = get_app()


@task(app, ignore_result=True, default_retry_delay=1,
      max_retries=5, bind=True)
class RepoTask(BaseTask):
    accepted_oprations = ["clone", "sync"]

    class RepoTaskError(TaskError):
        pass

    class UnknownRepoOperation(RepoTaskError):
        _default_message = "Unknown operation {}."

    def __init__(self, app, project, operation="sync", *args, **kwargs):
        super(self.__class__, self).__init__(app, *args, **kwargs)
        self.project, self.operation = project, operation
        if self.operation not in self.accepted_oprations:
            raise self.task_class.UnknownRepoOperation(self.operation)

    def run(self):
        try:
            result = getattr(self.project, self.operation)()
            logger.info(result)
        except Exception as error:
            self.app.retry(exc=error)


@task(app, ignore_result=True, bind=True)
class ScheduledTask(BaseTask):
    def __init__(self, app, job_id, *args, **kwargs):
        super(self.__class__, self).__init__(app, *args, **kwargs)
        self.job_id = job_id

    def run(self):
        from ..models import PeriodicTask
        try:
            task = PeriodicTask.objects.get(id=self.job_id)
        except PeriodicTask.DoesNotExist:
            return
        task.execute()


class _ExecuteAnsible(BaseTask):
    ansible_class = None

    def run(self):
        # pylint: disable=not-callable
        ansible_object = self.ansible_class(*self.args, **self.kwargs)
        ansible_object.run()


@task(app, ignore_result=True, bind=True)
class ExecuteAnsiblePlaybook(_ExecuteAnsible):
    ansible_class = AnsiblePlaybook


@task(app, ignore_result=True, bind=True)
class ExecuteAnsibleModule(_ExecuteAnsible):
    ansible_class = AnsibleModule


@task(app, ignore_result=True, bind=True)
class SendHook(BaseTask):
    def __init__(self, app, when, message, *args, **kwargs):
        super(self.__class__, self).__init__(app, *args, **kwargs)
        self.when = when
        self.message = message

    def run(self):
        Hook.objects.execute(self.when, self.message)
