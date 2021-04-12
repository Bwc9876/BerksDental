from django.conf import settings
from django import template
from django.template.defaultfilters import safe

register = template.Library()


@register.simple_tag(name="sitemaps")
def get_sitemap_links():
    hosts = settings.ALLOWED_HOSTS.copy()
    links = ""
    for host in hosts:
        links += f"Sitemap: http://{host}/sitemap.xml\n"
        links += f"Sitemap: https://{host}/sitemap.xml\n"
    return links
