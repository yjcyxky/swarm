from __future__ import absolute_import, unicode_literals
from celery import shared_task

@shared_task
def submit_job(task_uuid, advisor_setting, pkg_uuid, cobweb_setting):
    from ssadvisor.models import TaskPool, Task
    import uuid
    task = Task.objects.get(task_uuid = task_uuid)
    taskpool = TaskPool.objects.create(task_pool_uuid = uuid.uuid4(), task = task, job_id = 'test')
    taskpool.save()
