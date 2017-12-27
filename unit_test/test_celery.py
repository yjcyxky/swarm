#!/usr/bin/env python

from scouts.celery import debug_task
from ssadvisor.tasks import add

if __name__ == '__main__':
    import sys
    print(sys.path)
    print(debug_task.delay())
    print(add.delay(1, 2))
