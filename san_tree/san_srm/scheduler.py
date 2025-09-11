from apscheduler.schedulers.background import BackgroundScheduler
from .views import free_up_staff
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
    scheduler.start()
    print("Scheduler started!")
    atexit.register(lambda: scheduler.shutdown())
