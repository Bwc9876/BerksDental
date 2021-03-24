"""
    This file serves one purpose: have a list of path objects
    These path objects represent the links between url patterns and views
    We also add some additional urls if DEBUG is True
"""

from django.conf import settings
from django.urls import path, resolve, include

urlpatterns = [
    path('', include("main.urls")),
    path('admin/', include("edit.urls"))
]

print("Home App Name:" + resolve("/admin/").app_name)

# Media files (files uploaded by users) will be served as if they're static files (files like CSS and JS)
# This can result in security issues, so we only do this if DEBUG = True
# In production, we'll use pythonanywhere's system to serve the media files
# In addition, we add some debugging urls if DEBUG is True
if settings.DEBUG:
    from django.contrib import admin
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns.append(path('debug_admin/', admin.site.urls))
