from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from webpush import send_user_notification
from webpush.models import PushInformation

from accounts.models import CustomUsers
from san_srm.models import Service


def send_push_notification(username, title, message):
    try:
        user_obj = CustomUsers.objects.get(username=username)
    except CustomUsers.DoesNotExist:
        return

    push_infos = PushInformation.objects.filter(user=user_obj)

    subscriptions = [pi.subscription for pi in push_infos]

    for sub in subscriptions:
        try:
            payload = {
                "title": title,
                "body": message,
                "icon": "/static/images/icons/192X192.png",
            }
            send_user_notification(user=user_obj, payload=payload, ttl=1000)
        except Exception as e:
            print(f"Failed to send to subscription {sub.endpoint}: {e}")


# ----- Services -----
@receiver(post_save, sender=Service)
def service_notification(sender, instance, created, **kwargs):

    if created and instance.assigned_to:
        staff = instance.assigned_to
        if not staff:
            return

        send_push_notification(
            username=staff.username,
            title="New Service Assigned",
            message=f"You have a new service: {instance.service_type}",
        )


@receiver(post_save, sender=CustomUsers)
def handle_staff_vacant_status(sender, instance, created, update_fields=None, **kwargs):
    """
    When a staff member's status is updated to 'vacant',
    automatically try to assign a waiting service from the queue
    AFTER the transaction has been successfully committed.
    """
    # To avoid circular import issues
    from san_srm.views import assign_service_from_queue

    # We only care about existing 'User' roles being updated to 'vacant'
    if not created and instance.role == "User":
        if (update_fields and "status" in update_fields) or update_fields is None:
            if instance.status == "vacant":
                # Defer the queue assignment until after the current transaction commits.
                transaction.on_commit(lambda: assign_service_from_queue(instance))
