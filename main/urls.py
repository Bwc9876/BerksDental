"""
    This file defines the url patterns for the main app
    If DEBUG is true, we add the error view for testing
"""

from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from django.urls import path

from main import views, sitemaps

app_name = "main"

sitemaps = {
    'main': sitemaps.MainSiteMap
}

urlpatterns = [
    path('', views.home, name="home"),
    path('gallery/', views.gallery, name="gallery"),
    path('gallery-page/', views.get_gallery_page, name="gallery_page"),
    path('gallery/view/', views.view_photo, name="view_photo"),
    path('officers/', views.officers, name="officers"),
    path('events/', views.events, name="events"),
    path('about/', views.safe_render("about.html"), name="about"),
    path('unsupported/', views.safe_render("ie-card.html"), name="ie"),
    path('sitemap/', views.safe_render("sitemap.html"), name="sitemap"),
    path('sitemap.xml/', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt/', views.robots, name="robots")
]

if settings.DEBUG:
    urlpatterns.append(path('error/', views.test_error))
