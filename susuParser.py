import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from event import Event

HTML_PARSER = "html.parser"
CALENDAR_REQUEST_URL = "https://www.susu.org/php/ajax-calendar.php"

def datetimeToRequestFormat(valueToConvert):
    #Magic constants are... magic. This is simply the right format, sorry.
    return valueToConvert.isoformat()[0:19].replace("T"," ")

def requestCalForDay(date):
    formattedDate = datetimeToRequestFormat(date)
    requestParams = {"date": formattedDate, "list": "true", "week": "false"}
    request = requests.get(CALENDAR_REQUEST_URL, requestParams)
    request.raise_for_status()
    return request.text.encode('ascii', 'ignore')

def datetimeStringToObj(dtString):
    if not dtString: return None
    return datetime.strptime(dtString, "%Y-%m-%dT%H:%M:%S")

def parseEventListFromHtml(html):
    soup = BeautifulSoup(html, HTML_PARSER)
    eventListDivs = soup.select("#list")[0].find_all('div', recursive=False)

    eventList = list()
    for div in eventListDivs:
        nameTag = div.find("span", class_="eventname")
        if not nameTag: continue
        hostTag = div.find("span", class_="event_by")
        descTag = div.find("span", {"itemprop": "description"})
        startDateTag = div.find("time", {"itemprop": "startDate"})
        endDateTag = div.find("time", {"itemprop": "endDate"})
        #No idea why it's just 'name'
        locationTag = div.find("span", {"itemprop": "name"}) 

        event = Event()
        event.name = nameTag.string
        event.host = hostTag.string
        event.desc = descTag.string
        event.startDate = datetimeStringToObj(startDateTag['datetime'][0:19])
        event.endDate = datetimeStringToObj(endDateTag['datetime'][0:19])
        event.location = locationTag.string
        eventList.append(event)

    return eventList

def getEventsOnDay(date):
    return parseEventListFromHtml(requestCalForDay(date))

def dateperiod(startDate, days):
    for dayNumber in range(days-1):
        yield startDate + timedelta(dayNumber)
    
def getEventsInDatePeriod(startDate, days):
    events = list()
    for day in dateperiod(startDate, days):
        events.extend(getEventsOnDay(day))
    return events
    
#for event in getEventsInDatePeriod(currentDay, 10):
#    event.prettyPrint()
