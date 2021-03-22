from django.shortcuts import render
from django.views.decorators.http import require_safe

from edit import models


@require_safe
def home(request):
    featured_photos = models.GalleryPhoto.objects.filter(featured=True)
    return render(request, 'home.html', {'featuredPhotos': featured_photos})
