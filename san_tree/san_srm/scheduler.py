from apscheduler.schedulers.background import BackgroundScheduler
from .views import free_up_staff, free_up_onhold_staff, hold_service
import atexit
from apscheduler.triggers.interval import IntervalTrigger

scheduler = BackgroundScheduler(timezone="Asia/Kolkata")

def start():
    scheduler.add_job(
        func=free_up_staff,
        trigger=IntervalTrigger(seconds=30),
        id="free_up_staff_job",
        name="Free up staff every minute",
        replace_existing=True,
    )
    scheduler.add_job(
        func=free_up_onhold_staff,
        trigger=IntervalTrigger(seconds=30),
        id="free_up_onhold_staff_job",
        name="Free up on-hold staff every minute",
        replace_existing=True,
    )
    scheduler.add_job(
        func=hold_service,
        trigger=IntervalTrigger(seconds=30),
        id="hold_up_earlier_services",
        name="Hold services created earlier",
        replace_existing=True,
    )
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
