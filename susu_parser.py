import logging

from datetime import datetime, timedelta
import dateutil.parser
from dateutil.tz import tzutc

import requests
from bs4 import BeautifulSoup

from event import Event

HTML_PARSER = "html.parser"
CALENDAR_REQUEST_URL = "https://www.susu.org/php/ajax-calendar.php"
#The number of characters in the host's name starts in the HTML
HOST_NAME_START = 13


def datetime_to_request_format(value_to_convert):
    # Magic constants are... magic. This is simply the right format, sorry.
    return value_to_convert.isoformat()[0:19].replace("T", " ")


def request_cal_for_day(date):
    formatted_date = datetime_to_request_format(date)
    request_params = {"date": formatted_date, "list": "true", "week": "false"}

    #Make 3 (arbitrary number) attempts as the SUSU calendar sometimes
    #gives a random 404...
    for attempt in range(0, 3):
        try:
            logging.info("Retrieving calendar for {}, attempt {}".format(date, attempt))
            request = requests.get(CALENDAR_REQUEST_URL, request_params)
            request.raise_for_status()
            return request.text.encode('ascii', 'ignore')
        except requests.exceptions.HTTPError as e:
            logging.warning("Unable to retrieve SUSU calendar for {} on attempt {:.0f}".format(date, attempt))


def datetime_string_to_obj(dt_string):
    if not dt_string:
        return None
    new_datetime = dateutil.parser.parse(dt_string)
    if not new_datetime.tzinfo:
        return new_datetime.replace(tzinfo=tzutc())
    return new_datetime


def parse_event_list_from_html(html):
    soup = BeautifulSoup(html, HTML_PARSER)
    event_list_divs = soup.select("#list")[0].find_all('div', recursive=False)

    event_list = list()
    for div in event_list_divs:
        name_tag = div.find("span", class_="eventname")
        if not name_tag:
            continue
        host_tag = div.find("span", class_="event_by")
        desc_tag = div.find("span", {"itemprop": "description"})
        start_date_tag = div.find("time", {"itemprop": "startDate"})
        end_date_tag = div.find("time", {"itemprop": "endDate"})
        # No idea why it's just 'name'
        location_tag = div.find("span", {"itemprop": "name"})

        event = Event()
        event.name = name_tag.string
        event.host = host_tag.string[HOST_NAME_START:]
        event.desc = desc_tag.string
        event.start_date = datetime_string_to_obj(
            start_date_tag['datetime'])
        event.end_date = datetime_string_to_obj(end_date_tag['datetime'])
        event.location = location_tag.string
        event_list.append(event)

    return event_list


def get_events_on_day(date):
    return parse_event_list_from_html(request_cal_for_day(date))

def dateperiod(start_date, days):
    for day_number in range(days - 1):
        yield start_date + timedelta(day_number)


def get_events_in_date_period(start_date, days):
    events = list()
    for day in dateperiod(start_date, days):
        events.extend(get_events_on_day(day))
    return events
