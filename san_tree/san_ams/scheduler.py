from apscheduler.schedulers.background import BackgroundScheduler
from .views import LicenseUpdateView
import atexit
from apscheduler.triggers.interval import IntervalTrigger

scheduler = BackgroundScheduler(timezone="Asia/Kolkata")

def start():
    scheduler.add_job(
        func=LicenseUpdateView,
        trigger=IntervalTrigger(hours=24),
        id="license_update_job",
        name="Update licenses status daily",
        replace_existing=True,
    )
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
