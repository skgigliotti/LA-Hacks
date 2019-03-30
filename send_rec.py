#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 10:58:31 2019

@author: Dempsey
"""

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def sms_ahoy_reply():
    """Respond to incoming messages with a friendly SMS."""
    # Start our response
    #message_body = request.form['Body']
    resp = MessagingResponse()
    #print(message_body)

    # Add a message
    resp.message("Ahoy! Thanks so much for your message. You said: ")

    return str(resp)

""" Purpose: Allows student/requester to schedule an appointment. """
def schedule_appointment():
    return()

""" Purpose: Allows program to modify advisor's calender. """
def authenticate():
    return()

if __name__ == "__main__":
    app.run(debug=True)
