from apscheduler.schedulers.background import BackgroundScheduler
from .views import free_up_staff, free_up_onhold_staff
import atexit
from apscheduler.triggers.interval import IntervalTrigger

scheduler = BackgroundScheduler(timezone="Asia/Kolkata")

def start():
    scheduler.add_job(
        func=free_up_staff,
        trigger=IntervalTrigger(minutes=1),
        id="free_up_staff_job",
        name="Free up staff every minute",
        replace_existing=True,
    )
    scheduler.add_job(
        func=free_up_onhold_staff,
        trigger=IntervalTrigger(minutes=1),
        id="free_up_onhold_staff_job",
        name="Free up on-hold staff every minute",
        replace_existing=True,
    )
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
