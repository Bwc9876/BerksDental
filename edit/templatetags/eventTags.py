from datetime import date
from django import template

register = template.Library()


@register.simple_tag(name="makeDateObj", takes_context=True)
def make_date_obj(context):
    day = context.get("day")
    month = context.get("month")
    year = context.get("year")
    if day == 0:
        return None
    else:
        return date(year, month, day)


@register.simple_tag(name="getEventsOnDate", takes_context=True)
def get_events_on_day(context):
    results = []
    events = context.get("events")
    date_obj = context.get("date")
    for event in events:
        if event.startDate == date_obj or event.endDate == date_obj:
            results.append(event)
    return results
