from __future__ import absolute_import, unicode_literals
import os
import sys
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'swarm.settings')
app = Celery('swarm')

app.config_from_object(settings, namespace = 'CELERY')

app.autodiscover_tasks()

@app.task(bind = True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
