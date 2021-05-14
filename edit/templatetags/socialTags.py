"""
    This file contains tags and filters we can use for events
"""

from django import template

from edit.models import Social

register = template.Library()


@register.simple_tag(name="getSocials")
def get_socials():
    """
        This function gets all social objects in the db

        @return: A list of social objects
        @rtype: str
    """

    return Social.objects.all()
