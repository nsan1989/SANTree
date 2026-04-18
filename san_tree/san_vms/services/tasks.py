from celery import shared_task
from ..views import recurring_bookings


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=60,
    retry_kwargs={"max_retries": 3},
)
def recurring_bookings_task(self):
    recurring_bookings()
