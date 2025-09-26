from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from webpush import send_user_notification
from webpush.models import SubscriptionInfo, PushInformation
from accounts.models import CustomUsers

from .models import Complaint

def send_push_notification(username, title, message):
    """Send push notification to a specific username."""

    try:
        user_obj = CustomUsers.objects.get(username=username)
    except CustomUsers.DoesNotExist:
        print(f"User {username} does not exist")
        return

    push_infos = PushInformation.objects.filter(user=user_obj)

    subscriptions = [pi.subscription for pi in push_infos]
    print(f"Found {len(subscriptions)} subscriptions for {username}")

    for sub in subscriptions:
        try:
            payload = {
                "title": title,
                "body": message,
                "icon": "/static/images/icons/192X192.png"
            }
            send_user_notification(user=user_obj, payload=payload, ttl=1000)
            print(f"Sent notification to {user_obj.username} via subscription {sub.endpoint}")
        except Exception as e:
            print(f"Failed to send to subscription {sub.endpoint}: {e}")

# ----- Complaints -----
@receiver(post_save, sender=Complaint)
def complaint_notification(sender, instance, created, **kwargs):
    if created and instance.assigned_to:
        send_push_notification(
            username=instance.assigned_to.username,
            title="New Complaint Assigned",
            message=f"You have a new complaint: {instance.complaint_type}"
        )
