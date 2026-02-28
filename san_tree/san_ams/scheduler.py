import atexit

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .views import LicenseUpdateView

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
