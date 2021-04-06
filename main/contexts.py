from django.urls import resolve


def base_data(request):
    return {'app_name': resolve(request.path).app_name, "agent_type": request.META.get("HTTP_USER_AGENT", "None")}
