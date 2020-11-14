from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CartConfig(AppConfig):
    name = "donate_anything.cart"
    verbose_name = _("Cart")

    def ready(self):
        try:
            import donate_anything.cart.signals  # noqa F401
        except ImportError:
            pass
