from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import BlogPost


class StaticViewSitemap(Sitemap):
    """Public marketing pages.

    /training/ is deliberately absent — it's login-gated, so a crawler would
    only ever see the redirect. /smeta/ is public now, so it belongs here.
    """

    protocol = 'https'

    # Homepage is the entry point; service/case pages carry the commercial
    # intent; the rest are supporting.
    # /skills/ and /formats/ are 301s to /services/ now — a sitemap listing
    # redirects wastes crawl budget and looks like a stale map.
    PRIORITIES = {
        'pages:home': 1.0,
        'pages:services': 0.9,
        'pages:cases': 0.9,
        'pages:gallery': 0.8,
        'orders:constructor': 0.8,
        'pages:blog_index': 0.7,
        'pages:about': 0.6,
    }

    def items(self):
        return list(self.PRIORITIES)

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return self.PRIORITIES[item]

    def changefreq(self, item):
        return 'weekly' if item == 'pages:blog_index' else 'monthly'


class BlogSitemap(Sitemap):
    protocol = 'https'
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return BlogPost.objects.all()

    def location(self, post):
        return reverse('pages:blog_detail', args=[post.slug])


SITEMAPS = {
    'static': StaticViewSitemap,
    'blog': BlogSitemap,
}
