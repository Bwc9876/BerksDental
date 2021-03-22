from django.shortcuts import render
from django.views.decorators.http import require_safe

from edit import models


@require_safe
def home(request):
    featured_photos = models.GalleryPhoto.objects.filter(featured=True)
    return render(request, 'home.html', {'featuredPhotos': featured_photos})


@require_safe
def gallery(request):
    photos = models.GalleryPhoto.objects.all()
    return render(request, "gallery.html", {"photos": photos})


@require_safe
def officers(request):
    officers = models.Officer.objects.all()
    return render(request, "officers.html", {"officers": officers})