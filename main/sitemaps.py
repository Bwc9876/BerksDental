"""
    This file has the sitemap for the site, this sitemap generates an XML document for search engines
"""

from django.contrib import sitemaps
from django.urls import reverse

priorities = {
    'main:home': 1.0,
    'main:gallery': 0.8,
    'main:events': 0.7,
    'main:officers': 0.6,
    'main:about': 0.3
}

frequencies = {
    'main:about': 'never'
}


def get_priority(sitemap, item):
    return priorities.get(item, 0.5)


def get_frequency(sitemap, item):
    return frequencies.get(item, 'weekly')


class MainSiteMap(sitemaps.Sitemap):
    priority = get_priority
    changefreq = get_frequency
    protocol = 'https'

    def items(self):
        return ['main:home', 'main:gallery', 'main:officers', 'main:events', 'main:about']

    def location(self, item):
        return reverse(item)
