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
        "applied/organization/suggested/<int:pk>/",
        list.applied_organization_edits,
        name="applied-organization-edits",
    ),
    path(
        "applied/organization/suggested/<int:edit_pk>/viewed/",
        list.viewed_org_edit,
        name="mark-applied-org-edit-viewed",
    ),
    path(
        "applied/organization/edit/<int:pk>/",
        apply.applied_organization_update_view,
        name="edit-applied-org",
    ),
    path(
        "applied/organization/suggested/edit/",
        apply.suggest_edit_org_form_view,
        name="edit-suggest-applied-org",
    ),
    path("applied/business/<int:pk>/", list.applied_business, name="applied-business"),
    path(
        "applied/business/edit/<int:pk>/",
        apply.applied_business_update_view,
        name="edit-applied-bus",
    ),
    path(
        "applied/business/suggested/<int:pk>/",
        list.applied_business_edits,
        name="applied-business-edits",
    ),
    path(
        "applied/business/suggested/<int:edit_pk>/viewed/",
        list.viewed_bus_edit,
        name="mark-applied-bus-edit-viewed",
    ),
    path(
        "applied/business/suggested/edit/",
        apply.suggest_edit_bus_form_view,
        name="edit-suggest-applied-bus",
    ),
]
