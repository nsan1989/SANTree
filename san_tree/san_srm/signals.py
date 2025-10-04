from django.db.models.signals import post_save
from django.dispatch import receiver
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
                "icon": "/static/images/icons/192X192.png"
            }
            send_user_notification(user=user_obj, payload=payload, ttl=1000)
        except Exception as e:
            print(f"Failed to send to subscription {sub.endpoint}: {e}")

# ----- Services -----
@receiver(post_save, sender=Service)
def service_notification(sender, instance, created, **kwargs):
    if created and instance.assigned_to:
        shift_staffs = instance.assigned_to.shift_staffs.all()
        for staff in shift_staffs:
            send_push_notification(
                username=staff.username,
                title="New Service Assigned",
                message=f"You have a new service: {instance.service_type}"
            )
