import requests
from django.conf import settings

def send_sms(phone, service_type, from_location, to_location):
    url = "https://control.msg91.com/api/v5/flow"

    payload = {
        "template_id": settings.MSG91_SMS_TEMPLATE_ID,
        "short_url": 0,
        "recipients": [
            {
                "mobiles": f"91{phone}",
                "VAR1": service_type,
                "VAR2": from_location,
                "VAR3": to_location
            }
        ]
    }

    headers = {
        "accept": "application/json",
        "authkey": settings.MSG91_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers, timeout=5)
    return response.json()
