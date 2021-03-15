from django.conf import settings
from django.contrib import admin

from edit import models

# This file registers models to the admin feature of django, we'll only use the built-in admin feature for debugging

if settings.DEBUG:
    admin.site.register(models.ExternalLink)
    admin.site.register(models.GalleryPhoto)
    admin.site.register(models.Officer)
    admin.site.register(models.Event)
