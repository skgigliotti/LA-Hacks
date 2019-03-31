import os
from twilio.rest import Client

account_sid = 'AC561140658d26358c9d3829fc9f2c8072'
auth_token = '3dbae5df135e26232cd99c8a76cc76d7'

client = Client(account_sid, auth_token)


client.messages.create(to="+18054448834", from_="+18057386893", body = "ok world")
