"""
    This file contains tags and filters we can use for events
"""

from datetime import date

from django import template

register = template.Library()


@register.simple_tag(name="makeDateObj", takes_context=True)
def make_date_obj(context):
    """
    This function is used to make a date object from a month, day, and year

    @param context: A dict that should contain a month, day, and year value
    @type context: dict
    @return: A date object with the corresponding month, day, and year
    @rtype: date
    """

    day = context.get("day")
    month = context.get("month")
    year = context.get("year")
    if day == 0:
        return None
    else:
        return date(year, month, day)


@register.simple_tag(name="getEventsOnDate", takes_context=True)
def get_events_on_day(context):
    """
    This function is used to get events on a given day

    @param context: A dict that should contain a date we can check, and a list of events to pull from
    @type context: dict
    @return: The events on the given day
    @rtype: list
    """

    results = []
    events = context.get("events")
    date_obj = context.get("date")
    for event in events:
        if event.startDate == date_obj or event.endDate == date_obj:
            results.append(event)
    return results
