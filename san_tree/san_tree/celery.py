from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "san_tree.settings")

app = Celery("san_tree")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "free-up-staff-daytime": {
        "task": "san_srm.tasks.task_free_up_staff",
        "schedule": crontab(minute="*/1", hour="9-17"),
    },
    "free-up-onhold-staff-daytime": {
        "task": "san_srm.tasks.task_free_up_onhold_staff",
        "schedule": crontab(minute="*/1", hour="9-17"),
    },
    "hold-service-daytime": {
        "task": "san_srm.tasks.task_hold_service",
        "schedule": crontab(minute="*/1", hour="9-17"),
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
