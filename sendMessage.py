import os
from twilio.rest import Client

account_sid = ''
auth_token = ''
client = Client(account_sid,auth_token)

def send(message, toNumber):
    message = client.message \
        .create(
            body = message,
            from_ ='+16146666491',
            to=toNumber
        )