from django.urls import path
from django.views.generic import TemplateView

from donate_anything.charity.views import apply, list


app_name = "charity"
urlpatterns = [
    path("<int:pk>/", list.organization, name="organization"),
    path(
        "apply/",
        TemplateView.as_view(template_name="organization/apply/apply.html"),
        name="apply",
    ),
    path(
        "apply/organization/", apply.apply_organization_view, name="apply-organization"
    ),
    path("apply/business/", apply.apply_business_view, name="apply-business"),
    path(
        "applied/organization/<int:pk>/",
        list.applied_organization,
        name="applied-organization",
    ),
    path(
        "applied/organization/edit/<int:pk>/",
        apply.applied_organization_update_view,
        name="edit-applied-org",
    ),
    path("applied/business/<int:pk>/", list.applied_business, name="applied-business"),
    path(
        "applied/business/edit/<int:pk>/",
        apply.applied_business_update_view,
        name="edit-applied-bus",
    ),
]
