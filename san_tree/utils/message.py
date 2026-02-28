import requests
from django.conf import settings


def send_sms(phone, service_type, location_1, location_2):
    url = "https://control.msg91.com/api/v5/flow"

    payload = {
        "template_id": settings.MSG91_SMS_TEMPLATE_ID,
        "short_url": 0,
        "recipients": [
            {
                "mobiles": f"91{phone}",
                "var1": service_type,
                "var2": location_1,
                "var3": location_2,
            }
        ],
    }

    headers = {
        "accept": "application/json",
        "authkey": settings.MSG91_API_KEY,
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=payload, headers=headers, timeout=5)
    return response.json()
