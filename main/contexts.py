"""
    This file defines additional context to be sent to the template rendering engine
"""
from django.conf import settings
from django.urls import resolve


def base_data(request):
    """
    This context function provides useful data, such as the DEBUG, the protocol we're using, and the app name

    @param request: A django request object
    @type request: HttpRequest
    @return: Additional context to be sent to the templates
    @rtype: dict
    """

    return {'app_name': resolve(request.path).app_name, "agent_type": request.META.get("HTTP_USER_AGENT", "None"),
            "debug": settings.DEBUG, 'protocol': "http" if settings.DEBUG else "https"}
