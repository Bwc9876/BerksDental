import calendar
from datetime import date

from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import ValidationError
from django.http import Http404, JsonResponse
from django.shortcuts import render, get_object_or_404
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
    links = models.ExternalLink.objects.all()
    return render(request, 'home.html', {'featuredPhotos': featured_photos, 'upcomingEvents': upcoming_events, 'external_links': links})


MAX_IMAGES_PER_PAGE = 12


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
    view_link_base = reverse("main:view_photo")
    photos = [
        {'id': photo.id, 'src': photo.photo_link(), 'link': f"{view_link_base}?id={photo.id}", 'alt': photo.caption,
         'height': photo.height, 'width': photo.width}
        for photo in target_list]
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
    first_page = photo_paginator.get_page(1)
    first_list = models.GalleryPhoto.objects.all()[0:first_page.end_index()]
    return render(request, "gallery.html", {"photos": first_list, 'hasNext': first_page.has_next()})


def get_next_photo(photo):
    try:
        return models.GalleryPhoto.objects.exclude(date_posted=photo.date_posted).filter(
            date_posted__gte=photo.date_posted).order_by("date_posted")[0]
    except IndexError:
        return None


def get_last_photo(photo):
    try:
        return models.GalleryPhoto.objects.exclude(date_posted=photo.date_posted).filter(
            date_posted__lte=photo.date_posted).order_by("-date_posted")[0]
    except IndexError:
        return None


@require_safe
def view_photo(request):
    target_id = request.GET.get("id", "")
    try:
        target_photo = get_object_or_404(models.GalleryPhoto, id=target_id)
        next_photo = get_next_photo(target_photo)
        last_photo = get_last_photo(target_photo)
        next_link = None if next_photo is None else f"{reverse('main:view_photo')}?id={next_photo.id}"
        last_link = None if last_photo is None else f"{reverse('main:view_photo')}?id={last_photo.id}"
        return render(request, "photo_view.html",
                      {"photo": target_photo, "next_link": next_link, "last_link": last_link})
    except ValidationError:
        raise Http404()


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


def get_next_and_previous_links(month, year, view_type):
    next_month, next_year = get_next_month_and_year(month, year)
    next_link = f"{reverse('main:events')}?month={next_month}&year={next_year}&view={view_type}"
    last_month, last_year = get_last_month_and_year(month, year)
    previous_link = f"{reverse('main:events')}?month={last_month}&year={last_year}&view={view_type}"
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

    if view_type == "calendar" or view_type == "list":
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
            next_link, previous_link = get_next_and_previous_links(month, year, view_type)
            return render(request, f"events-{view_type}.html",
                          {"events": matching_events, "weeks": month_calendar, 'today': today, "month": month,
                           "month_name": month_name, "year": year,
                           "next_link": next_link, "previous_link": previous_link,
                           "weekdays": ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]})
        except calendar.IllegalMonthError:
            raise Http404("Invalid Month")
        except ValueError:
            raise Http404("Invalid Month/Year")
    else:
        raise Http404("Invalid View Type")


def safe_render(template_name, ctx=None):
    """ This function is used as a shortcut to render the given html file and require that the request type is GET

    :returns: A view function that can be used in a path object to render an HTML file
    :rtype: function(request) -> HttpResponse
    """

    if ctx is None:
        ctx = {}

    @require_safe
    def render_view(request):
        return render(request, template_name, ctx)

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
