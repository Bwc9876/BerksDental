"""
    This file contains tags and filters we can use in templates
"""

from django import template
from django.forms.fields import CheckboxInput
from django.template.defaultfilters import safe, title

from edit.forms import PhotoField

register = template.Library()

alertIcons = {
    'error': "exclamation-circle",
    'success': "check-circle",
    'warning': "exclamation-triangle",
    'info': "info-circle"
}


@register.simple_tag(name="action")
def action(name, url, icon, size="h4", show_name=False, new_tab=False):
    tab_target = "target=\"_blank\""
    return safe(
        f'<a aria-label="{title(name)}" {tab_target if new_tab else ""} class="{name} {"labeled" if show_name else ""} navigation-action" href="{url}">'
        f'<i class="fas {name}-icon {icon} {size}">{title(name) if show_name else ""}'
        f'</i>'
        f'</a>')


@register.simple_tag(name="getAlertIcon")
def get_alert_icon(request):
    alert_type = get_alert_type(request)
    return alertIcons.get(alert_type, alertIcons["error"])


@register.simple_tag(name="getAlert")
def get_alert(request):
    return request.GET.get("alert", None)


@register.simple_tag(name="getAlertType")
def get_alert_type(request):
    return request.GET.get("alertType", "error")


@register.simple_tag(name="getPrimaryValue")
def get_primary_value(target_object):
    return target_object[0]


@register.filter(name='is_checkbox')
def is_checkbox(field):
    return field.field.widget.__class__.__name__ == CheckboxInput().__class__.__name__


@register.simple_tag(name="needsMultiPart")
def needs_multipart(form):
    for field in form.fields.values():
        if field.widget.__class__.__name__ == PhotoField().__class__.__name__:
            return True
    return False
