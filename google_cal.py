import httplib2
import os
import math
import logging

from apiclient import discovery
from apiclient.http import BatchHttpRequest
import oauth2client
from oauth2client import client
from oauth2client import tools

from datetime import datetime
from dateutil.tz import tzutc
import dateutil.parser

import susu_parser as susu
from event import Event

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Calendar Event Pusher'
CALENDAR_ID = 'gofflsctss3evrv2valc138nl0@group.calendar.google.com'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('./')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatability with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_calendar_service():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    return discovery.build('calendar', 'v3', http=http)


def to_google_format(event):
    return {
        'summary': str(event.name),
        'location': str(event.location),
        'description': str(event.desc),
        'start': {
            'dateTime': event.start_date.isoformat(),
        },
        'end': {
            'dateTime': event.end_date.isoformat(),
        },
        'extendedProperties': {
            'shared': {
                'host': str(event.host)
            }
        }
    }

def google_format_to_event(src_event):
    event = Event()
    event.name = src_event.get('summary', '')
    event.location = src_event.get('location', '')
    event.desc = src_event.get('description', '')
    event.start_date = dateutil.parser.parse(src_event['start']['dateTime'])
    event.end_date = dateutil.parser.parse(src_event['end']['dateTime'])
    event.host = src_event.get('extendedProperties', {}).get('shared', {}).get('host', '')
    return event

MAX_BATCH_SIZE = 50
def send_multiple_requests(requests):
    request_queue = list(requests)
    current_batch = BatchHttpRequest()
    current_batch_size = 0
    while len(request_queue):
        current_batch.add(request_queue.pop(0))
        current_batch_size += 1
        if current_batch_size >= MAX_BATCH_SIZE:
            current_batch.execute()
            current_batch = BatchHttpRequest()
            current_batch_size = 0
    current_batch.execute()


def mk_req_insert_event(service, event):
    return service.events().insert(
        calendarId=CALENDAR_ID,
        body=to_google_format(event))

def insert_event(service, event):
    logging.info("Inserting {0} into calendar.", event.name)
    response = mk_req_insert_event(service, event).execute()
    print('Event created: %s' % (response.get('htmlLink')))

def insert_event_list(service, events):
    logging.info("Inserting {0:d} events into calendar.", len(events))
    requests = list()
    for event in events:
        requests.append(mk_req_insert_event(service, event))
    send_multiple_requests(requests)

G_API_MAX_RESULTS = 1000
def mk_req_list_events(service, startDate, pageToken=""):
    return service.events().list(
        calendarId=CALENDAR_ID,
        maxResults=G_API_MAX_RESULTS,
        timeMin=startDate.isoformat(),
        pageToken=pageToken)

def list_events_raw(service, startDate):
    response = mk_req_list_events(service, startDate).execute()
    items = response.get('items', [])
    nextPageToken = response.get('nextPageToken', None)
    while nextPageToken:
        print(nextPageToken)
        response = mk_req_list_events(service, startDate, nextPageToken).execute()
        items.extend(response.get('items', []))
        nextPageToken = response.get('nextPageToken', None)
    return items

def list_events(service, start_date):
    return [google_format_to_event(event) for event 
            in list_events_raw(service, start_date)]

def mk_req_delete_event(service, eventId):
    return service.events().delete(calendarId=CALENDAR_ID,eventId=eventId)

def delete_all(service):
    today = datetime.now(tzutc())
    logging.info("Deleting all calendar items after %s", str(today))
    requests = list()
    events = list_events_raw(service, datetime.now(tzutc()))
    for event in events:
        google_format_to_event(event).pretty_print()
        requests.append(mk_req_delete_event(service, event['id']))
    send_multiple_requests(requests)

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    logging.basicConfig(level="INFO")
    service = get_calendar_service()
    delete_all(service)
    events = susu.get_events_in_date_period(datetime.now(tzutc()), 60)
    insert_event_list(service, events)

if __name__ == '__main__':
    main()
