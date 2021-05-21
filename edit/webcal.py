"""
    This file sets up the use of the webcal protocol
    It allows users to sync our calendar with a service of their choice
    They do this via a link
"""

import os
from datetime import datetime, date, time, timedelta

from django.conf import settings
from icalendar import Calendar
from icalendar import Event as CalendarEvent, vText, vDuration

from edit.models import Event

CALENDAR_PATH = settings.MEDIA_ROOT + "event-calendar/" + settings.ICAL_FILE_NAME + ".ics"
CALENDAR_URL = settings.MEDIA_URL + "event-calendar/" + settings.ICAL_FILE_NAME + ".ics"


def setup_calendar():
    """
    This function sets up a calendar object with some required attributes

    @return: A new Calendar that's properly configured
    @rtype: Calendar
    """

    cal = Calendar()
    cal.add('prodid', '-//Berks Dental Assistant Society Webpage//mxm.dk//')
    cal.add('version', '2.0')
    cal.add('X-WR-CALNAME', "Berks Dental Assistants Society")
    cal.add('name', "Berks Dental Assistants Society")
    cal.add("X-WR-CALDESC", "Events relating to the Berks Dental Assistants Society")
    cal.add("description", "Events relating to the Berks Dental Assistants Society")
    cal.add("X-WR-TIMEZONE", "America/New_York")
    cal.add("timezone-id", "America/New_York")
    cal.add("color", "dodgerblue")
    cal.add('refresh-interval', vDuration(timedelta(hours=12)))
    if not settings.DEBUG:
        cal.add('url', f"webcal://{settings.ALLOWED_HOSTS[0]}/{CALENDAR_URL}")
    return cal


def write_calendar(cal, path=CALENDAR_PATH):
    """
    This function saves a calendar object to a file

    @param path: path to the calendar file
    @type path: str
    @param cal: The calendar to save
    @type cal: Calendar
    """

    if not os.path.exists(settings.MEDIA_ROOT + "event-calendar/"):
        os.mkdir(settings.MEDIA_ROOT + "event-calendar/")
    with open(path, 'wb+') as calendar_file:
        calendar_file.write(cal.to_ical())


def combine(date_object, time_object):
    """
    This is a quick utility function to combine a date and a time object into a datetime object

    @param date_object: The date to add
    @type date_object: date
    @param time_object: The time to add
    @type time_object: time
    @return: the new datetime object
    @rtype: datetime
    """

    return datetime.combine(date_object, time_object)


def make_calendar_event(event):
    """
    Creates an Event object based off our Event model

    @param event: The event to read data from
    @type event: Event
    @return: the Event object to be added to the calendar
    @rtype: CalendarEvent
    """

    calendar_event = CalendarEvent()
    calendar_event.add("uid", vText(str(event.id)))
    calendar_event.add("summary", vText(event.name))
    calendar_event.add("dtstart", combine(event.startDate, event.startTime))
    calendar_event.add("dtend", combine(event.endDate, event.endTime))
    calendar_event.add("dtstamp", datetime.now())
    calendar_event.add("description", vText(event.description))
    calendar_event.add("location", vText(event.link) if event.virtual else vText(event.location))
    return calendar_event


def update_file(path=CALENDAR_PATH):
    """
    This file updates the calendar file from all events
    This can be resource heavy, so only run it after a change

    @param path: the path to the calendar file
    @type path: str
    @return: the path to the file that was saved
    @rtype: str
    """

    events = Event.objects.all()
    cal = setup_calendar()
    for event in events:
        calendar_event = make_calendar_event(event)
        cal.add_component(calendar_event)
    write_calendar(cal, path=path)
    return CALENDAR_PATH
