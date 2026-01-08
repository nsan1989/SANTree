from celery import shared_task
import time
from .views import free_up_staff, free_up_onhold_staff, hold_service

@shared_task
def task_free_up_staff():
    free_up_staff()

@shared_task
def task_free_up_onhold_staff():
    free_up_onhold_staff()

@shared_task
def task_hold_service():
    hold_service()
