import os
from twilio.rest import Client

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
from_number = '+18332759949'
client = Client(account_sid, auth_token)

def send(message_body, toNumber, success=True):
    
    if success:
        message = client.messages \
            .create(
                body = message_body,
                from_ = from_number,
                to=toNumber
            )

        message = client.messages \
            .create(
                body = "Share the number if you enjoy!",
                from_ = from_number,
                to = toNumber
            )

    else:
        message = client.messages \
            .create(
                body = message_body,
                from_ = from_number,
                to=toNumber
            )