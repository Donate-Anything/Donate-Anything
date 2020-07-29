from allauth.account.views import LoginView
from axes.decorators import axes_dispatch, axes_form_invalid
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.utils.decorators import method_decorator
from django.views import defaults as default_views
from django.views.generic import TemplateView

from donate_anything.users.forms import AxesLoginForm


LoginView.dispatch = method_decorator(axes_dispatch)(LoginView.dispatch)
LoginView.form_invalid = method_decorator(axes_form_invalid)(LoginView.form_invalid)


urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path(
        "about/", TemplateView.as_view(template_name="pages/about.html"), name="about"
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("donate_anything.users.urls", namespace="users")),
    path(
        "accounts/login/",
        LoginView.as_view(form_class=AxesLoginForm),
        name="account_login",
    ),
    path("accounts/", include("allauth.urls")),
    # Custom urls includes go here
    path("item/", include("donate_anything.item.urls", namespace="item")),
    path("organization/", include("donate_anything.charity.urls", namespace="charity")),
    path("forum/", include("donate_anything.forum.urls", namespace="forum")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
