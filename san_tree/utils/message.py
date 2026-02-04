import requests
from django.conf import settings

def send_sms(phone, service_type, location_1, location_2):
    url = "https://api.msg91.com/api/v2/sendsms"

    message = (
        f"You have received a {service_type} service request "
        f"from {location_1} to {location_2}."
    )

    payload = {
        "sender": settings.MSG91_SENDER_ID,
        "route": "4",              # Transactional
        "country": "91",
        "sms": [
            {
                "message": message,
                "to": [phone]
            }
        ]
    }

    headers = {
        "Authkey": settings.MSG91_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()
