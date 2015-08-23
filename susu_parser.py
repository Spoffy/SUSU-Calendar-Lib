import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from event import Event

HTML_PARSER = "html.parser"
CALENDAR_REQUEST_URL = "https://www.susu.org/php/ajax-calendar.php"


def datetime_to_request_format(valueToConvert):
    # Magic constants are... magic. This is simply the right format, sorry.
    return valueToConvert.isoformat()[0:19].replace("T", " ")


def request_cal_for_day(date):
    formattedDate = datetime_to_request_format(date)
    requestParams = {"date": formattedDate, "list": "true", "week": "false"}
    request = requests.get(CALENDAR_REQUEST_URL, requestParams)
    request.raise_for_status()
    return request.text.encode('ascii', 'ignore')


def datetime_string_to_obj(dtString):
    if not dtString:
        return None
    return datetime.strptime(dtString, "%Y-%m-%dT%H:%M:%S")


def parse_event_list_from_html(html):
    soup = BeautifulSoup(html, HTML_PARSER)
    eventListDivs = soup.select("#list")[0].find_all('div', recursive=False)

    eventList = list()
    for div in eventListDivs:
        nameTag = div.find("span", class_="eventname")
        if not nameTag:
            continue
        hostTag = div.find("span", class_="event_by")
        descTag = div.find("span", {"itemprop": "description"})
        startDateTag = div.find("time", {"itemprop": "startDate"})
        endDateTag = div.find("time", {"itemprop": "endDate"})
        # No idea why it's just 'name'
        locationTag = div.find("span", {"itemprop": "name"})

        event = Event()
        event.name = nameTag.string
        event.host = hostTag.string
        event.desc = descTag.string
        event.startDate = datetime_string_to_obj(
            startDateTag['datetime'][0:19])
        event.endDate = datetime_string_to_obj(endDateTag['datetime'][0:19])
        event.location = locationTag.string
        eventList.append(event)

    return eventList


def get_events_on_day(date):
    return parse_event_list_from_html(request_cal_for_day(date))


def dateperiod(startDate, days):
    for dayNumber in range(days - 1):
        yield startDate + timedelta(dayNumber)


def get_events_in_date_period(startDate, days):
    events = list()
    for day in dateperiod(startDate, days):
        events.extend(get_events_on_day(day))
    return events

# for event in get_events_in_date_period(currentDay, 10):
#    event.prettyPrint()

get_events_in_date_period(datetime.today(), 1)
