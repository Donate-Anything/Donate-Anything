from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ItemConfig(AppConfig):
    name = "donate_anything.item"
    verbose_name = _("Item")

    def ready(self):
        try:
            import donate_anything.item.signals  # noqa F401
        except ImportError:
            pass
