from django.http import JsonResponse
from django.db.models.signals import post_save
from django.dispatch import receiver
from webpush import send_user_notification
from webpush.models import PushInformation
from accounts.models import CustomUsers
from san_srm.models import Service
from utils.message import send_sms
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

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
        staff = getattr(instance.assigned_to, "shift_staffs", None)
        if not staff:
            return
        
        send_push_notification(
            username=instance.assigned_to.shift_staffs.username,
            title="New Service Assigned",
            message=f"You have a new service: {instance.service_type}"
        )

        if staff.phone_number:
            send_sms(
                phone=staff.phone_number,
                service_type=instance.service_type,
                location_1=instance.location_1,
                location_2=instance.location_2
            )

#------ SMS ------
@csrf_exempt
@require_POST
def send_sms_view(request):
    try:
        data = json.loads(request.body)

        phone = data.get("phone")
        service_type = data.get("service_type")
        location_1 = data.get("location_1")
        location_2 = data.get("location_2")

        if not all([phone, service_type, location_1, location_2]):
            return JsonResponse(
                {
                    "error": "phone, service_type, location_1, location_2 are required"
                },
                status=400
            )

        response = send_sms(
            phone=phone,
            service_type=service_type,
            location_1=location_1,
            location_2=location_2
        )

        return JsonResponse({
            "message": "SMS sent successfully",
            "msg91_response": response
        })

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON body"},
            status=400
        )

    except Exception as e:
        return JsonResponse(
            {"error": str(e)},
            status=500
        )
