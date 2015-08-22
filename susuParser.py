import requests
from bs4 import BeautifulSoup
from datetime import datetime

HTML_PARSER = "html.parser"
CALENDAR_REQUEST_URL = "https://www.susu.org/php/ajax-calendar.php"

currentDay = datetime.today()

class Event:
    def __init__(self):
        self.name = "Default Name"
        self.host = "No host found"
        self.desc = "No description found"
        self.startDate = None
        self.endDate = None
        self.location = "No location found"

    def prettyPrint(self):
        print("Name: ", str(self.name))
        print("Host: ", str(self.host))
        print("Desc: ", str(self.desc))
        print("Start Date: ", str(self.startDate))
        print("End Date: ", str(self.endDate))
        print("Location: ", str(self.location))

def datetimeToRequestFormat(valueToConvert):
    #Magic constants are... magic. This is simply the right format, sorry.
    return valueToConvert.isoformat()[0:19].replace("T"," ")

def requestCalendarForDay(date):
    formattedDate = datetimeToRequestFormat(date)
    requestParams = {"date": formattedDate, "list": "true", "week": "false"}
    return requests.get(CALENDAR_REQUEST_URL, requestParams)

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
        event.startDate = startDateTag['datetime']
        event.endDate = endDateTag['datetime']
        event.location = locationTag.string
        eventList.append(event)

    return eventList

    
for event in parseEventListFromHtml(requestCalendarForDay(currentDay).text):
    event.prettyPrint()
