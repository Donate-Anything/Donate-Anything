from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "donate_anything.users"
    verbose_name = _("Users")

    def ready(self):
        patch_rate_limit()
        try:
            import donate_anything.users.signals  # noqa F401
        except ImportError:
            pass


# noinspection PyPackageRequirements,PyProtectedMember
def patch_rate_limit():
    from axes.helpers import get_client_ip_address
    from ratelimit.core import _SIMPLE_KEYS, ip_mask

    def user_or_ip(request):
        if request.user.is_authenticated:
            return str(request.user.pk)
        return ip_mask(get_client_ip_address(request))

    _SIMPLE_KEYS["ip"] = lambda r: ip_mask(get_client_ip_address(r))
    _SIMPLE_KEYS["user_or_ip"] = user_or_ip
