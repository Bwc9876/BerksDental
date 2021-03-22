"""
    This file serves one purpose: have a list of path objects
    These path objects represent the links between url patterns and views
    We also add some additional urls if DEBUG is True
"""


from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from main import views as main_views
from edit import views as edit_views
from django.conf import settings
from django.conf.urls.static import static

# Main URL config, this is the list read by django that determines what links go to what view
urlpatterns = [
    path('', main_views.home, name="home"),
    path('gallery', main_views.gallery, name="gallery"),
    path('officers', main_views.officers, name="officers"),
    path('admin/', edit_views.admin_home, name="admin_home"),
    path('admin/login/', LoginView.as_view(template_name="login.html", redirect_authenticated_user=True), name="login"),
    path('admin/logout/', LogoutView.as_view(), name="logout")
]

urlpatterns += edit_views.setup_viewsets()

# Media files (files uploaded by users) will be served as if they're static files (files like CSS and JS)
# This can result in security issues, so we only do this if DEBUG = True
# In production, we'll use pythonanywhere's system to serve the media files
# In addition, we add some debugging urls if DEBUG is True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns.append(path('debug_admin/', admin.site.urls))

