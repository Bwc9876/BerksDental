from django.urls import path
from main import views
from django.conf import settings

app_name = "main"
urlpatterns = [
    path('', views.home, name="home"),
    path('gallery/', views.gallery, name="gallery"),
    path('officers/', views.officers, name="officers"),
    path('events/', views.events, name="events"),
    path('about/', views.safe_render("about.html"), name="about")
]

if settings.DEBUG:
    urlpatterns.append(path('error/', views.test_error))
