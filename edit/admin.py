"""
    This file registers models to the admin feature of django, we'll only use the built-in admin feature for debugging
"""

from django.conf import settings


if settings.DEBUG:
    from edit import models
    from django.contrib import admin
    from django.contrib.auth.admin import UserAdmin

    class CustomUserAdmin(UserAdmin):
        model = models.User

    admin.site.register(models.User, CustomUserAdmin)
    admin.site.register(models.ExternalLink)
    admin.site.register(models.GalleryPhoto)
    admin.site.register(models.Officer)
    admin.site.register(models.Event)
    admin.site.register(models.Social)
