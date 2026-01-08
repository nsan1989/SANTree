from celery import shared_task
import time
from .views import free_up_staff, free_up_onhold_staff, hold_service

@shared_task
def task_free_up_staff(*args, **kwargs):
    result = free_up_staff()
    return f"task_free_up_staff done: {result}"

@shared_task
def task_free_up_onhold_staff(*args, **kwargs):
    result = free_up_onhold_staff()
    return f"task_free_up_onhold_staff done: {result}"

@shared_task
def task_hold_service(*args, **kwargs):
    result = hold_service()
    return f"task_hold_service done: {result}"
