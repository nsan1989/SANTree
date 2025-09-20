from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from webpush import send_user_notification
from webpush.models import SubscriptionInfo

from .models import Tasks

def send_push_notification(username, title, message):
    """Helper to send push notification to a specific username."""
    subscriptions = SubscriptionInfo.objects.filter(webpush_info=username)
    print(f"Found {subscriptions.count()} subscriptions for {username}")
    for sub in subscriptions:
        try:
            user_obj = User.objects.get(username=sub.webpush_info)
            print(f"Sending notification to {user_obj.username}")
            payload = {
                "head": title,
                "body": message,
                "icon": "/static/images/icons/192X192.png"
            }
            send_user_notification(user=user_obj, payload=payload, ttl=1000)
        except User.DoesNotExist:
            print(f"User not found for subscription {sub.endpoint}")
            continue

@receiver(post_save, sender=Tasks)
def task_notification(sender, instance, created, **kwargs):
    if created and instance.assigned_to:
        send_push_notification(
            username=instance.assigned_to.username,
            title="New Task Assigned",
            message=f"You have a new task: {instance.title}"
        )
        