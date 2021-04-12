"""
    This file contains tags and filters we can use in templates
"""

from django import template
from django.template.defaultfilters import safe

register = template.Library()

alertIcons = {
    'error': "exclamation-circle",
    'success': "check-circle",
    'warning': "exclamation-triangle",
    'info': "info-circle"
}


@register.simple_tag(name="action")
def action(name, url, icon, size="fa-lg"):
    return safe(
        f'<a class="{name} navigationAction" href="{url}"><i class="fas {name}-icon {icon} {size}">'
        f'</i></a>')


@register.simple_tag(name="getAlertIcon")
def get_alert_icon(request):
    alert_type = get_alert_type(request)
    return alertIcons.get(alert_type, "error")


@register.simple_tag(name="getAlert")
def get_alert(request):
    return request.GET.get("alert", None)


@register.simple_tag(name="getAlertType")
def get_alert_type(request):
    return request.GET.get("alertType", "error")
