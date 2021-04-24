from django.shortcuts import redirect
from django.urls import reverse, resolve


def trident_redirect(get_response):
    def middleware(request):
        if "Trident" in request.META.get("HTTP_USER_AGENT", "None"):
            if resolve(request.path).url_name != "ie":
                return redirect(reverse("main:ie"))
            else:
                return get_response(request)
        else:
            return get_response(request)

    return middleware
