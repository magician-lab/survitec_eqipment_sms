import os
import requests

TAIFA_URL = "https://api.taifamobile.co.ke/v2/sms/sendsms"


def send_sms(mobile, message):

    response = requests.post(
        TAIFA_URL,
        headers={
            "h_api_key": os.getenv("TAIFA_API_KEY")
        },
        json={
            "mobile": mobile,
            "sender_name": os.getenv(
                "TAIFA_SENDER_NAME"
            ),
            "message": message
        },
        timeout=30
    )

    return response.json()

