from __future__ import absolute_import
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import setproctitle
from bin import configuration as conf

def post_worker_init(dummy_worker):
    setproctitle.setproctitle(
        conf.GUNICORN_WORKER_READY_PREFIX + setproctitle.getproctitle()
    )
