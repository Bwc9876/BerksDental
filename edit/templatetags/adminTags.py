"""
    This file contains tags and filters we can use in admin
"""

from django import template
from django.forms.fields import CheckboxInput
from django.template.defaultfilters import safe, title, slugify

from edit.forms import PhotoField

register = template.Library()

alertIcons = {
    'error': "exclamation-circle",
    'success': "check-circle",
    'warning': "exclamation-triangle",
    'info': "info-circle"
}


@register.simple_tag(name="action")
def action(name, url, icon, size="h4", show_name=False, new_tab=False, enabled=True):
    """
    This function is used to generate HTML for an action

    @param name: The name of the action
    @type name: str
    @param url: The url the action leads to
    @type url: str
    @param icon: The fontawesome icon class to show
    @type icon: str
    @param size: The size (class) of the icon
    @type size: str
    @param show_name: Whether to show the name of the action next to the icon
    @type show_name: bool
    @param new_tab: Whether to open the url in a new tab
    @type show_name: bool
    @param enabled: If the action is enables
    @type enabled: bool
    @return: An HTML String that represents the action
    @rtype: str
    """

    tab_target = "target=\"_blank\""
    return safe(
        f'<a aria-label="{title(name)}" {tab_target if new_tab else ""} class="{"" if enabled else "disabled"}'
        f' {slugify(name)} {"labeled" if show_name else ""} navigation-action" href="{url}">'
        f'<i class="fas {icon} {slugify(name)}-icon {size}">{title(name) if show_name else ""}'
        f'</i>'
        f'</a>')


@register.simple_tag(name="getAlertIcon")
def get_alert_icon(request):
    """
    This function is used to get the icon (font-awesome class) of an alert

    @param request: A Django request
    @return: The icon for an alert box
    @rtype: str
    """

    alert_type = get_alert_type(request)
    return alertIcons.get(alert_type, alertIcons["error"])


@register.simple_tag(name="getAlert")
def get_alert(request):
    """
    This function is used to get an alert message

    @param request: A Django request
    @return: The text for an alert box
    @rtype: str
    """

    return request.GET.get("alert", None)


@register.simple_tag(name="getAlertType")
def get_alert_type(request):
    """
    This function is used to get the type of alert (for coloring) of an alert box

    @param request: A Django request
    @return: The type of alert for an alert box
    @rtype: str
    """

    return request.GET.get("alertType", "error")


@register.simple_tag(name="getPrimaryValue")
def get_primary_value(target_object):
    """
    This function is used exclusively to get the primary value of an object list for accessibility

    @param target_object: The object we want to get the primary value of
    @type target_object: tuple
    @return: The primary value of the object
    @rtype: str
    """

    return target_object[0]


@register.filter(name='is_checkbox')
def is_checkbox(field):
    """
    This function is used to check if a given field is a checkbox

    @param field: The field to check
    @type field: Field
    @return: Whether it's a checkbox
    @rtype: bool
    """

    return field.field.widget.__class__.__name__ == CheckboxInput().__class__.__name__


@register.filter(name="needs_multi_part")
def needs_multipart(form):
    """
    This function is used to check if a form's enctype needs to be set to multipart
    That is, when the user needs to upload an image

    @param form: The form to check
    @type form: Form
    @return: Whether we need multipart enctype
    @rtype: bool
    """

    for field in form.fields.values():
        if field.widget.__class__.__name__ == PhotoField().__class__.__name__:
            return True
    return False
