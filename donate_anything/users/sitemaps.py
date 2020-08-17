from django.contrib import sitemaps
from django.urls import reverse


_items = (
    "home",
    "about",
    "roadmap",
    "forum:home",
    "charity:apply",
    "account_login",
    "account_signup",
)
_priority = (1.0, 0.3, 0.6, 0.5, 0.7, 0.4, 0.4)


class StaticViewSitemap(sitemaps.Sitemap):
    changefreq = "daily"
    protocol = "https"

    def items(self):
        return _items

    def priority(self, item):
        return _priority[_items.index(item)]

    def location(self, item):
        return reverse(item)
