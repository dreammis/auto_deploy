from __future__ import absolute_import, unicode_literals

import os
from multiprocessing import current_process

from celery import Celery
from celery.signals import worker_process_init

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "auto_deploy.settings")

app = Celery("auto_deploy")

app.config_from_object("django.conf:settings")


@worker_process_init.connect
def fix_multiprocessing(**kwargs):
    try:
        current_process()._config
    except AttributeError:
        current_process()._config = {'semprefix': '/mp'}
