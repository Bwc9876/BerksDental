import calendar
from datetime import date

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.template.exceptions import TemplateDoesNotExist
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_safe, require_http_methods

from edit import models


@require_safe
def home(request):
    """ This view function gets many objects from the database and uses them to render home.html
    We use @require_safe to make sure only GET requests are allowed

    :param request: A request object sent by django
    :type request: class:`django.http.HttpRequest`
    :returns: An HttpResponse containing the rendered html file
    :rtype: class:`django.http.HttpResponse` 
    """

    featured_photos = models.GalleryPhoto.objects.filter(featured=True)
    upcoming_events = models.Event.objects.filter(startDate__gte=date.today()).order_by("startDate")[:5]
    return render(request, 'home.html', {'featuredPhotos': featured_photos, 'upcomingEvents': upcoming_events})


MAX_IMAGES_PER_PAGE = 20


@csrf_exempt
@require_http_methods(["POST"])
def get_gallery_page(request):
    target_page_number = request.POST.get("page", 1)
    photo_objects = models.GalleryPhoto.objects.all()
    photo_paginator = Paginator(photo_objects, MAX_IMAGES_PER_PAGE, allow_empty_first_page=True)
    target_page = photo_paginator.get_page(target_page_number)
    start = target_page.start_index() - 1
    if start < 0:
        start = 0
    target_list = list(photo_objects[start:target_page.end_index()])
    photos = [{'link': photo.photo_link(), 'alt': photo.caption} for photo in target_list]
    return JsonResponse({'photos': photos, 'hasNext': target_page.has_next()})


@require_safe
def gallery(request):
    """ This view function gets gallery photo objects from the database and uses them to render gallery.html
    We use @require_safe to make sure only GET requests are allowed

    :param request: A request object sent by django
    :type request: class:`django.http.HttpRequest`
    :returns: An HttpResponse containing the rendered html file
    :rtype: class:`django.http.HttpResponse` 
    """

    photo_objects = models.GalleryPhoto.objects.all()
    photo_paginator = Paginator(photo_objects, MAX_IMAGES_PER_PAGE, allow_empty_first_page=True)
    first_list = models.GalleryPhoto.objects.all()[0:photo_paginator.get_page(1).end_index()]
    return render(request, "gallery.html", {"photos": first_list})


@require_safe
def officers(request):
    """ This view function gets officers from the database and uses them to render officers.html
    We use @require_safe to make sure only GET requests are allowed

    :param request: A request object sent by django
    :type request: class:`django.http.HttpRequest`
    :returns: An HttpResponse containing the rendered html file
    :rtype: class:`django.http.HttpResponse` 
    """

    officer_objects = models.Officer.objects.all()
    return render(request, "officers.html", {"officers": officer_objects})


def get_last_month_and_year(month, year):
    if month == 1:
        return 12, year - 1
    else:
        return month - 1, year


def get_next_month_and_year(month, year):
    if month == 12:
        return 1, year + 1
    else:
        return month + 1, year


def get_next_and_previous_links(month, year):
    next_month, next_year = get_next_month_and_year(month, year)
    next_link = f"{reverse('main:events')}?month={next_month}&year={next_year}"
    last_month, last_year = get_last_month_and_year(month, year)
    previous_link = f"{reverse('main:events')}?month={last_month}&year={last_year}"
    return next_link, previous_link


@require_safe
def events(request):
    """ This view function gets events from the database and uses them to render events-list.html
    We use @require_safe to make sure only GET requests are allowed

    :param request: A request object sent by django
    :type request: class:`django.http.HttpRequest`
    :returns: An HttpResponse containing the rendered html file
    :rtype: class:`django.http.HttpResponse` 
    """
    view_type = request.GET.get("view", "calendar")

    if view_type == "calendar":
        try:
            calendar.setfirstweekday(calendar.SUNDAY)
            today = date.today()
            month = int(request.GET.get("month", today.month))
            year = int(request.GET.get("year", today.year))
            month_calendar = calendar.monthcalendar(year, month)
            month_name = calendar.month_name[month]
            matching_events = models.Event.objects.filter(
                (Q(startDate__month=month) & Q(startDate__year=year)) | (
                        Q(endDate__month=month) & Q(endDate__year=year)))
            next_link, previous_link = get_next_and_previous_links(month, year)
            return render(request, "events-calendar.html",
                          {"events": matching_events, "weeks": month_calendar, 'today': today, "month": month,
                           "month_name": month_name, "year": year,
                           "next_link": next_link, "previous_link": previous_link})
        except calendar.IllegalMonthError:
            raise Http404("Invalid Month")
        except ValueError:
            raise Http404("Invalid Month/Year")
    elif view_type == "list":
        upcoming_events = models.Event.objects.filter(startDate__gte=date.today()).order_by("startDate")
        past_events = models.Event.objects.filter(startDate__lt=date.today()).order_by("-startDate")
        return render(request, "events-list.html", {"upcoming": upcoming_events, "past": past_events})
    else:
        raise Http404("Invalid view type")


def safe_render(template_name):
    """ This function is used as a shortcut to render the given html file and require that the request type is GET

    :returns: A view function that can be used in a path object to render an HTML file
    :rtype: function(request) -> HttpResponse
    """

    @require_safe
    def render_view(request):
        return render(request, template_name)

    return render_view


@require_safe
def test_error(request):
    """ This function is used as a way to test how error pages will look in production
    While debugging, whenever there's an error, django will always show a stacktrace
    So, we set up this url while debugging that allows us to see how error pages will look

    :param request: A request object sent by django
    :type request: class:`django.http.HttpRequest`
    :returns: An HttpResponse containing the rendered html file
    :rtype: class:`django.http.HttpResponse`
    """

    try:
        error_type = int(request.GET.get("type", "404"))
        return render(request, f"{error_type}.html")
    except ValueError:
        raise Http404()
    except TemplateDoesNotExist:
        raise Http404()


def robots(request):
    return render(request, "robots.txt", content_type="text/plain")
