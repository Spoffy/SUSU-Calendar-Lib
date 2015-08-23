import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

import susu_parser as susu
from event import Event
from datetime import datetime
from dateutil.tz import tzutc
import dateutil.parser

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




def insert_event(service, event):
    event = service.events().insert(
        calendarId=CALENDAR_ID,
        body=to_google_format(event)).execute()
    print('Event created: %s' % (event.get('htmlLink')))

G_API_MAX_RESULTS = 2500
def list_events(service, startDate):
    response = service.events().list(
        calendarId=CALENDAR_ID,
        maxResults=G_API_MAX_RESULTS,
        timeMin=startDate.isoformat()).execute()
    return response.get('items', [])


def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    service = get_calendar_service()
    events = list_events(service, datetime.now(tzutc()))
    for event in events:
        google_format_to_event(event).pretty_print()


if __name__ == '__main__':
    main()
