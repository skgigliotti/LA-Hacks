#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 10:58:31 2019

@author: Dempsey
"""

from __future__ import print_function
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import datetime
import pickle
import os
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import firebase_admin
from firebase_admin import credentials

from firebase_admin import firestore


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def sms_request():
    #send msg to the server to get appt times back
    resp = MessagingResponse()
    msg = request.values.get('Body')
    #resp.message(get_hours(msg))
    #resp.message(get_slots(msg))
    params = msg.split(None, 1)
    print(params)
    resp.message(check_slot(params[0], params[1]))

    resp = MessagingResponse()
    msg = request.values.get('Body').lower().strip()
    if (msg == 'office hours'):
        name = request.values.get('Body').strip()
        resp.message(get_hours(name))

    if (msg == 'appt' or msg == 'appointment'):
        name = request.values.get('Body').strip()
        resp.message(get_slots(name))
        resp.message("Please select a time and enter it in the format DOW Month Day Time")
        time = request.values.get('Body')
        valid = check_slot(name,time)
        while(valid == "false"):
            resp.message("Sorry, the time has been taken. Please choose again.")
            resp.message(get_slots(name))
        resp.message("Congratulations. You have made an appointment")
    return str(resp)



""" Purpose: Get office hours based on Professor's last name. """
def get_hours(lastname):
    professor_ref= db.collection(u'Professors').where(u'`last name`', u'==', lastname).limit(1)
    professors = professor_ref.get()

    for p in professors:
        return("{}".format(p.get(u'phone')))
    #my_dict = { el.id: el.to_dict() for el in professor }
    #print(my_dict)

    #return('results: {}'.format(professor.to_dict()))
""" Purpose: Allows student/requester to schedule an appointment. """
def schedule_appointment():
    event = {
      'summary': 'LA Hacks',
      'location': '800 Howard St., San Francisco, CA 94103',
      'description': 'A chance to hear more about Google\'s developer products.',
      'start': {
        'dateTime': '2019-03-30T09:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
      },
      'end': {
        'dateTime': '2019-03-30T17:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
      },
      'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=2'
      ],
      'attendees': [
        {'email': 'roroku@westmont.edu'},
        {'email': 'sbrin@example.com'},
      ],
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'email', 'minutes': 24 * 60},
          {'method': 'popup', 'minutes': 10},
        ],
      },
    }

    #event = service.events().insert(calendarId='primary', body=event).execute()
    print ('Event created: %s' % (event.get('htmlLink')))

    # Call the Calendar API

    return()

""" Purpose: Allows program to modify advisor's calender. """
def authenticate():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return(creds)


""" Purpose: Get office hours based on Professor's last name. """
def get_hours(lastname):
    info = ''

    try:
        professors_ref = db.collection(u'Professors').where(u'`last name`', u'==', lastname)
        professors = professors_ref.get()

        for p in professors:
            days = p.reference.collection(u'Days').get()
            for d in days:
                info = info + '{}: '.format(d.get(u'day'))
                info = info + '{}\n'.format(d.get(u'`office hours`'))
            info = info + '{}'.format(p.get(u'office'))
    except: #google.cloud.exceptions.NotFound:
        print(u'No such document!')

    return(info)

def get_slots(lastname):
    info = ''
    professors_ref = db.collection(u'Professors').where(u'`last name`', u'==', lastname)
    professors = professors_ref.get()

    for p in professors:
        days = p.reference.collection(u'Days').get()
        for d in days:
            slots = d.reference.collection(u'StartTimes').order_by(u'time').get()
            for s in slots:
                info = info + '{} '.format(d.get(u'day'))
                info = info + '{}\n'.format(s.get(u'time'))
        info = info + '{}'.format(p.get(u'office'))

    return(info)

def check_slot(lastname, slot):
    available = 'false'
    params = slot.split() # 0: day of week, 1: month 2: day, 3: time
    print(params)

    professors_ref = db.collection(u'Professors').where(u'`last name`', u'==', lastname)
    professors = professors_ref.get()

    """ check entered appointment slot exists """
    if (len(params) == 4): # user should have entered 4 arguments
        for p in professors:
            days = p.reference.collection(u'Days').get()
            if('{}'.format(p.get(u'`last name`')) == lastname):
                for d in days:
                    if('{}'.format(d.get(u'day')) == params ):
                        slots = d.reference.collection(u'StartTimes').order_by(u'time').get()
                        for s in slots:
                            if('{}'.format(s.get(u'time')) == params[3]):
                                available = 'true'
                                break

    return(available)

if __name__ == "__main__":
    cred = credentials.Certificate('la-hacks-63a19-4ac45eadbfb8.json')
    firebase_admin.initialize_app(cred, {
        'projectId': 'la-hacks-63a19',
    })

    db = firestore.client()
    """
    doc_ref = db.collection(u'Professors').document()
    doc_ref.set({
        u'last name': u'Patterson',
        u'first name': u'Donald',
        u'office': u'WH-305',
        u'phone' : u'18051234567',
        u'department':u'Computer Science'
    })

    doc_ref = db.collection(u'Professors').document()
    doc_ref.set({
        u'last name': u'Hunter',
        u'first name': u'David',
        u'office': u'WH-301',
        u'phone' : u'18055671234',
        u'department':u'Mathematics'
    })

    doc_ref = db.collection(u'Professors').document()
    doc_ref.set({
        u'last name': u'Cardoso',
        u'first name': u'Dinora',
        u'office': u'REY-202',
        u'phone' : u'18052349998',
        u'department':u'Spanish'
    })

    doc_ref = db.collection(u'Professors').document()
    doc_ref.set({
        u'last name': u'Anderson',
        u'first name': u'Scott',
        u'office': u'ADM-104',
        u'phone' : u'18054649998',
        u'department':u'Art'
    })

    doc_ref = db.collection(u'Professors').document()
    doc_ref.set({
        u'last name': u'Mallampalli',
        u'first name': u'Chandra',
        u'office': u'DNE-205',
        u'phone' : u'18054649998',
        u'department':u'History'
    })
    """
    """
    doc_ref = db.collection(u'Professors').document()
    doc_ref.set({
        u'last name': u'Patterson',
        u'first name': u'Donald',
        u'office': u'WH-305',
        u'phone' : u'18051234567',
        u'department':u'Computer Science'


    })
    doc_ref2 = doc_ref.collection(u'Days').document(u'Wednesday')
    doc_ref2.set({
        u'day': u'Wed'
    })
    doc_ref3 = doc_ref2.collection(u'StartTimes').document()
    doc_ref3.set({
        u'time': u'9'
    })

    doc_ref = db.collection(u'Professors').document()
    doc_ref.set({
        u'last name': u'Hunter',
        u'first name': u'David',
        u'office': u'WH-301',
        u'phone' : u'18055671234',
        u'department':u'Mathematics'
    })
    doc_ref2 = doc_ref.collection(u'Days').document(u'Friday')
    doc_ref2.set({
        u'day': u'Fri'
    })
    doc_ref3 = doc_ref2.collection(u'StartTimes').document()
    doc_ref3.set({
        u'time': u'15'
    })

    doc_ref = db.collection(u'Professors').document()
    doc_ref.set({
        u'last name': u'Cardoso',
        u'first name': u'Dinora',
        u'office': u'REY-202',
        u'phone' : u'18052349998',
        u'department':u'Spanish'
    })
    doc_ref2 = doc_ref.collection(u'Days').document(u'Wednesday')
    doc_ref2.set({
        u'day': u'Wed'
    })
    doc_ref3 = doc_ref2.collection(u'StartTimes').document()
    doc_ref3.set({
        u'time': u'12'
    })

    doc_ref = db.collection(u'Professors').document()
    doc_ref.set({
        u'last name': u'Anderson',
        u'first name': u'Scott',
        u'office': u'ADM-104',
        u'phone' : u'18054649998',
        u'department':u'Art'
    })
    doc_ref2 = doc_ref.collection(u'Days').document(u'Monday')
    doc_ref2.set({
        u'day': u'Mon'
    })
    doc_ref3 = doc_ref2.collection(u'StartTimes').document()
    doc_ref3.set({
        u'time': u'15'
    })
    doc_ref2 = doc_ref.collection(u'Days').document(u'Friday')
    doc_ref2.set({
        u'day': u'Fri'
    })
    doc_ref3 = doc_ref2.collection(u'StartTimes').document()
    doc_ref3.set({
        u'time': u'16'
    })

    doc_ref = db.collection(u'Professors').document()
    doc_ref.set({
        u'last name': u'Docter',
        u'first name': u'Mary',
        u'office': u'REY-205',
        u'phone' : u'18054649998',
        u'department':u'Spanish'
    })
    doc_ref2 = doc_ref.collection(u'Days').document(u'Wednesday')
    doc_ref2.set({
        u'day': u'Wed'
    })
    doc_ref3 = doc_ref2.collection(u'StartTimes').document()
    doc_ref3.set({
        u'time': u'15'
    })
    """
    #print(get_hours('Anderson'))
    #creds = authenticate() # get credentials for google account
    #service = build('calendar', 'v3', credentials=creds) # manipulate google calendar
    #schedule_appointment()
    app.run(debug=True)
