import requests
import bs4
from datetime import datetime

calendarRequestUrl = "https://www.susu.org/php/ajax-calendar.php"

currentDay = datetime.today()

def datetimeToRequestFormat(valueToConvert):
    #Magic constants are... magic. This is simply the right format, sorry.
    return valueToConvert.isoformat()[0:19].replace("T"," ")

def requestCalendarDay(date):
    formattedDate = datetimeToRequestFormat(date)
    requestParams = {"date": formattedDate, "list": "true", "week": "false"}
    return requests.get(calendarRequestUrl, requestParams)

print(requestCalendarDay(currentDay).text)
print(requestCalendarDay(currentDay).url)

