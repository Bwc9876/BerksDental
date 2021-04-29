"""
    This file contains custom middleware, which is run between receving a request, and sending the response
"""

from django.shortcuts import redirect
from django.urls import reverse, resolve


def trident_redirect(get_response):
    """
    If the user agent of the request uses Trident,
    we send them to a page informing them that they're browser isn't supported

    @param get_response: A function to get the response from a request
    @type get_response: function
    @return: The middleware function
    @rtype: function
    """

    def middleware(request):
        if "Trident" in request.META.get("HTTP_USER_AGENT", "None"):
            if resolve(request.path).url_name != "ie":
                return redirect(reverse("main:ie"))
            else:
                return get_response(request)
        else:
            return get_response(request)

    return middleware
