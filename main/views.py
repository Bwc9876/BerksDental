from datetime import date
from django.http import Http404
from django.shortcuts import render
from django.template.exceptions import TemplateDoesNotExist
from django.views.decorators.http import require_safe

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
    return render(request, "gallery.html", {"photos": photo_objects})


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


@require_safe
def events(request):
    """ This view function gets events from the database and uses them to render events.html
    We use @require_safe to make sure only GET requests are allowed

    :param request: A request object sent by django
    :type request: class:`django.http.HttpRequest`
    :returns: An HttpResponse containing the rendered html file
    :rtype: class:`django.http.HttpResponse` 
    """

    upcoming_events = models.Event.objects.filter(startDate__gte=date.today())
    past_events = models.Event.objects.filter(startDate__lt=date.today())
    return render(request, "events.html", {"upcoming": upcoming_events, "past": past_events})


def safe_render(templateName):
    """ This function is used as a shortcut to render the given html file and require that the request type is GET

    :returns: A view function that can be used in a path object to render an html file
    :rtype: function(request) -> HttpResponse
    """

    @require_safe
    def render_view(request):
        return render(request, templateName)

    return render_view


@require_safe
def test_error(request):
    """ This function is used as a way to test how error pages will look in production
    While debugging, whenever there's an error, django will always show a stacktrace
    So, we setup this url while debugging that allows us to see how error pages will look

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
