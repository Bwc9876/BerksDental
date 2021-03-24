"""
    This file contains tags and filters we can use in templates
"""

from django import template

from edit.models import Social

register = template.Library()


@register.simple_tag(name="getSocials")
def get_socials():
    """ This is a template tag used to get every social object from the db in order to render it in the footer

    :returns: A list of social media objects
    :rtype: list(:class:`edit.models.Social`)
    """

    return Social.objects.all()
