"""
    This file registers models to the admin feature of django, we'll only use the built-in admin feature for debugging
"""

from django.conf import settings

from edit import models

if settings.DEBUG:
    from django.contrib import admin

    admin.site.register(models.ExternalLink)
    admin.site.register(models.GalleryPhoto)
    admin.site.register(models.Officer)
    admin.site.register(models.Event)
    admin.site.register(models.Social)
