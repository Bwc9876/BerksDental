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
from edit.webcal import CALENDAR_URL


@require_safe
def home(request):
    """
    This view function renders the home page

    @param request: A django request object
    @type request: HttpRequest
    @return: A response to the request
    @rtype: HttpResponse
    """

    featured_photos = models.GalleryPhoto.objects.filter(featured=True)
    upcoming_events = models.Event.objects.filter(startDate__gte=date.today()).order_by("startDate")[:3]
    links = models.ExternalLink.objects.all()
    return render(request, 'home.html',
                  {'featuredPhotos': featured_photos, 'upcomingEvents': upcoming_events, 'external_links': links,
                   'hide_home_link': True})


MAX_IMAGES_PER_PAGE = 12


@csrf_exempt
@require_http_methods(["POST"])
def get_gallery_page(request):
    """
    This view is to be called via AJAX to get more photos to load in the gallery page

    @param request: A django request object
    @type request: HttpRequest
    @return: A json object that has the photos, and whether there are more photos to load
    @rtype: JsonResponse
    """

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
    """
    This view renders the gallery page, it only renders a few images at first,
    but you can render more via a button

    @param request: A django request object
    @type request: HttpRequest
    @return: A response to the request
    @rtype: HttpResponse
    """

    photo_objects = models.GalleryPhoto.objects.all()
    photo_paginator = Paginator(photo_objects, MAX_IMAGES_PER_PAGE, allow_empty_first_page=True)
    first_page = photo_paginator.get_page(1)
    first_list = models.GalleryPhoto.objects.all()[0:first_page.end_index()]
    return render(request, "gallery.html", {"photos": first_list, 'hasNext': first_page.has_next()})


def get_last_photo(photo, featured_only):
    """
    This function is used by photo_view to get the previous photo relative to another photo

    @param photo: The photo to check
    @type photo: models.GalleryPhoto
    @param featured_only: whether to only get featured photos
    @type featured_only: bool
    @return: The previous photo object, if any
    @rtype: models.GalleryPhoto
    """

    try:
        query = models.GalleryPhoto.objects.exclude(date_posted=photo.date_posted).filter(
            date_posted__gte=photo.date_posted).order_by("date_posted")
        if featured_only:
            return query.filter(featured=True)[0]
        else:
            return query[0]
    except IndexError:
        return None


def get_next_photo(photo, featured_only):
    """
    This function is used by photo_view to get the next photo relative to another photo

    @param photo: The photo to check
    @type photo: models.GalleryPhoto
    @param featured_only: whether to only get featured photos
    @type featured_only: bool
    @return: The next photo object, if any
    @rtype: models.GalleryPhoto
    """

    try:
        query = models.GalleryPhoto.objects.exclude(date_posted=photo.date_posted).filter(
            date_posted__lte=photo.date_posted).order_by("-date_posted")
        if featured_only:
            return query.filter(featured=True)[0]
        else:
            return query[0]
    except IndexError:
        return None


@require_safe
def view_photo(request):
    """
    This view renders a specific photo and lets you go to the next or the previous

    @param request: A django request object
    @type request: HttpRequest
    @return: A response to the request
    @rtype: HttpResponse
    """

    target_id = request.GET.get("id", "")
    featured = request.GET.get("featured", "no")
    featured_only = featured == "yes"
    try:
        target_photo = get_object_or_404(models.GalleryPhoto, id=target_id)
        next_photo = get_next_photo(target_photo, featured_only)
        last_photo = get_last_photo(target_photo, featured_only)
        next_link = None if next_photo is None else f"{reverse('main:view_photo')}" \
                                                    f"?id={next_photo.id}&featured={featured}"
        last_link = None if last_photo is None else f"{reverse('main:view_photo')}" \
                                                    f"?id={last_photo.id}&featured={featured}"
        return render(request, "photo_view.html",
                      {"photo": target_photo, "next_link": next_link, "last_link": last_link})
    except ValidationError:
        raise Http404()


@require_safe
def officers(request):
    """
    This view renders the officers and displays their info

    @param request: A django request object
    @type request: HttpRequest
    @return: A response to the request
    @rtype: HttpResponse
    """

    officer_objects = models.Officer.objects.all()
    return render(request, "officers.html", {"officers": officer_objects})


def get_last_month_and_year(month, year):
    """
    Given a month and year, get the previous month and year

    @param month: the month to use
    @type month: int
    @param year: the year to use
    @type year: int
    @return: The previous month and year
    @rtype: int, int
    """

    if month == 1:
        return 12, year - 1
    else:
        return month - 1, year


def get_next_month_and_year(month, year):
    """
    Given a month and year, get the next month and year

    @param month: the month to use
    @type month: int
    @param year: the year to use
    @type year: int
    @return: The next month and year
    @rtype: int, int
    """

    if month == 12:
        return 1, year + 1
    else:
        return month + 1, year


def get_next_and_previous_links(month, year, view_type):
    """
    Get the previous and next links for the event view

    @param month: the current month
    @type month: int
    @param year: the current year
    @type year: int
    @param view_type: the view type (calendar or list)
    @type view_type: str
    @return: The link to the next and previous month
    @rtype: str, str
    """

    next_month, next_year = get_next_month_and_year(month, year)
    next_link = f"{reverse('main:events')}?month={next_month}&year={next_year}&view={view_type}"
    last_month, last_year = get_last_month_and_year(month, year)
    previous_link = f"{reverse('main:events')}?month={last_month}&year={last_year}&view={view_type}"
    return next_link, previous_link


@require_safe
def events(request):
    """
    This view renders events to either a calendar, or a list view

    @param request: A django request object
    @type request: HttpRequest
    @return: A response to the request
    @rtype: HttpResponse
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
                           "weekdays": ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"], 'ics_link': CALENDAR_URL})
        except calendar.IllegalMonthError:
            raise Http404("Invalid Month")
        except ValueError:
            raise Http404("Invalid Month/Year")
    else:
        raise Http404("Invalid View Type")


def safe_render(template_name, ctx=None):
    """
    This function is used as a shortcut to generate a view that renders a given html file safely

    @param template_name: the name of the html file
    @param ctx: additional context to pass
    @return: a view function that renders the given html file
    @rtype: function
    """

    if ctx is None:
        ctx = {}

    @require_safe
    def render_view(request):
        return render(request, template_name, ctx)

    return render_view


@require_safe
def test_error(request):
    """
    This view is used in debugging to see how error pages will look

    @param request: A django request object
    @type request: HttpRequest
    @return: A response to the request
    @rtype: HttpResponse
    """

    try:
        error_type = int(request.GET.get("type", "404"))
        return render(request, f"{error_type}.html")
    except ValueError:
        raise Http404()
    except TemplateDoesNotExist:
        raise Http404()


def robots(request):
    """
    This view renders robots.txt for search engines

    @param request: A django request object
    @type request: HttpRequest
    @return: A response to the request
    @rtype: HttpResponse
    """

    return render(request, "robots.txt", content_type="text/plain")
