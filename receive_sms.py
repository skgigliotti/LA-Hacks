import os
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse


app = Flask(__name__)

@app.route("/sms", methods=['GET','POST'])
def sms_reply():
    resp = MessagingResponse()

    #resp.message("automated response")

    msg = request.values.get('Body').lower().strip()
    #res = MessagingResponse()
    if msg == "matcha":
        resp.message("noice")
    else:
        resp.message("meh")

    return str(resp)

@app.route("/")
def home():
    return("Hello world")


if __name__ == "__main__":
    app.run()
