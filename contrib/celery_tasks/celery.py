from __future__ import absolute_import, unicode_literals
from celery import Celery, Task
import os, json

def get_config():
    config = {}
    working_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    with open(os.path.join(working_dir, "config.json"), "r") as f:
        config.update(json.load(f))
    return config

config = get_config()
celery_config = config.get("CELERY_SETTINGS")
CELERY_BACKEND = celery_config.get("backend")
CELERY_BROKER = celery_config.get("broker")

app = Celery('celery_tasks', backend = CELERY_BACKEND, broker = CELERY_BROKER,
                    include = ['celery_tasks.package'])

app.conf.update(
    result_expires = 3600,
)

if __name__ == '__main__':
    app.start()
