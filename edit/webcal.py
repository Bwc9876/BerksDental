import os
from datetime import datetime

from django.conf import settings
from icalendar import Calendar
from icalendar import Event as CalendarEvent, vText

from edit.models import Event

CALENDAR_PATH = settings.MEDIA_ROOT + "event-calendar/" + settings.ICAL_FILE_NAME + ".ics"
CALENDAR_URL = settings.MEDIA_URL + "event-calendar/" + settings.ICAL_FILE_NAME + ".ics"


def setup_calendar():
    cal = Calendar()
    cal.add('prodid', '-//Berks Dental Assistant Society Events//mxm.dk//')
    cal.add('version', '2.0')
    return cal


def write_calendar(cal):
    if not os.path.exists(settings.MEDIA_ROOT + "event-calendar/"):
        os.mkdir(settings.MEDIA_ROOT + "event-calendar/")
    with open(CALENDAR_PATH, 'wb+') as calendar_file:
        calendar_file.write(cal.to_ical())


def combine(date, time):
    return datetime.combine(date, time)


def make_calendar_event(event):
    calendar_event = CalendarEvent()
    calendar_event.add("uid", vText(str(event.id)))
    calendar_event.add("summary", vText(event.name))
    calendar_event.add("dtstart", combine(event.startDate, event.startTime))
    calendar_event.add("dtend", combine(event.endDate, event.endTime))
    calendar_event.add("description", vText(event.description))
    calendar_event.add("location", vText(event.link) if event.virtual else vText(event.location))
    return calendar_event


def update_file():
    events = Event.objects.all()
    cal = setup_calendar()
    for event in events:
        calendar_event = make_calendar_event(event)
        cal.add_component(calendar_event)
    write_calendar(cal)
    return CALENDAR_PATH
