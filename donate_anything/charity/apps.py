from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CharityConfig(AppConfig):
    name = "donate_anything.charity"
    verbose_name = _("Charity")

    def ready(self):
        try:
            import donate_anything.charity.signals  # noqa F401
        except ImportError:
            pass
