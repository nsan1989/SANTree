import requests
from django.conf import settings

def send_sms(phone, var1, var2, var3):
    url = "https://control.msg91.com/api/v5/flow"

    payload = {
        "template_id": settings.MSG91_SMS_TEMPLATE_ID,
        "short_url": 0,
        "recipients": [
            {
                "mobiles": f"91{phone}",
                "VAR1": var1,
                "VAR2": var2,
                "VAR3": var3
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
