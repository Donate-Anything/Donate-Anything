import pytest
from django.urls import resolve, reverse


pytestmark = pytest.mark.django_db


def test_organization_view(charity):
    assert (
        reverse("charity:organization", kwargs={"pk": charity.id})
        == f"/organization/{charity.id}/"
    )
    assert resolve(f"/organization/{charity.id}/").view_name == "charity:organization"


def test_apply():
    assert reverse("charity:apply") == "/organization/apply/"
    assert resolve("/organization/apply/").view_name == "charity:apply"


def test_apply_organization():
    assert reverse("charity:apply-organization") == "/organization/apply/organization/"
    assert (
        resolve("/organization/apply/organization/").view_name
        == "charity:apply-organization"
    )


def test_apply_business():
    assert reverse("charity:apply-business") == "/organization/apply/business/"
    assert (
        resolve("/organization/apply/business/").view_name == "charity:apply-business"
    )


def test_applied_organization(organization_application):
    assert (
        reverse(
            "charity:applied-organization", kwargs={"pk": organization_application.id}
        )
        == f"/organization/applied/organization/{organization_application.id}/"
    )
    assert (
        resolve(
            f"/organization/applied/organization/{organization_application.id}/"
        ).view_name
        == "charity:applied-organization"
    )


def test_applied_organization_edit(organization_application):
    assert (
        reverse("charity:edit-applied-org", kwargs={"pk": organization_application.id})
        == f"/organization/applied/organization/edit/{organization_application.id}/"
    )
    assert (
        resolve(
            f"/organization/applied/organization/edit/{organization_application.id}/"
        ).view_name
        == "charity:edit-applied-org"
    )


def test_show_organization_app_edits(organization_application):
    assert (
        reverse(
            "charity:applied-organization-edits",
            kwargs={"pk": organization_application.id},
        )
        == f"/organization/applied/organization/suggested/{organization_application.id}/"
    )
    assert (
        resolve(
            f"/organization/applied/organization/suggested/{organization_application.id}/"
        ).view_name
        == "charity:applied-organization-edits"
    )


def test_applied_business(business_application):
    assert (
        reverse("charity:applied-business", kwargs={"pk": business_application.id})
        == f"/organization/applied/business/{business_application.id}/"
    )
    assert (
        resolve(f"/organization/applied/business/{business_application.id}/").view_name
        == "charity:applied-business"
    )


def test_applied_business_edit(business_application):
    assert (
        reverse("charity:edit-applied-bus", kwargs={"pk": business_application.id})
        == f"/organization/applied/business/edit/{business_application.id}/"
    )
    assert (
        resolve(
            f"/organization/applied/business/edit/{business_application.id}/"
        ).view_name
        == "charity:edit-applied-bus"
    )


def test_show_business_app_edits(business_application):
    assert (
        reverse(
            "charity:applied-business-edits", kwargs={"pk": business_application.id}
        )
        == f"/organization/applied/business/suggested/{business_application.id}/"
    )
    assert (
        resolve(
            f"/organization/applied/business/suggested/{business_application.id}/"
        ).view_name
        == "charity:applied-business-edits"
    )


def test_mark_org_suggested_edit_viewed(organization_application_suggested_edit):
    assert (
        reverse(
            "charity:mark-applied-org-edit-viewed",
            kwargs={"edit_pk": organization_application_suggested_edit.id},
        )
        == f"/organization/applied/organization/suggested/{organization_application_suggested_edit.id}/viewed/"
    )
    assert (
        resolve(
            f"/organization/applied/organization/suggested/{organization_application_suggested_edit.id}/viewed/"
        ).view_name
        == "charity:mark-applied-org-edit-viewed"
    )


def test_mark_bus_suggested_edit_viewed(business_application_suggested_edit):
    assert (
        reverse(
            "charity:mark-applied-bus-edit-viewed",
            kwargs={"edit_pk": business_application_suggested_edit.id},
        )
        == f"/organization/applied/business/suggested/{business_application_suggested_edit.id}/viewed/"
    )
    assert (
        resolve(
            f"/organization/applied/business/suggested/{business_application_suggested_edit.id}/viewed/"
        ).view_name
        == "charity:mark-applied-bus-edit-viewed"
    )


def test_edit_suggested_org():
    assert (
        reverse("charity:edit-suggest-applied-org",)
        == "/organization/applied/organization/suggested/edit/"
    )
    assert (
        resolve("/organization/applied/organization/suggested/edit/").view_name
        == "charity:edit-suggest-applied-org"
    )


def test_edit_suggested_bus():
    assert (
        reverse("charity:edit-suggest-applied-bus",)
        == "/organization/applied/business/suggested/edit/"
    )
    assert (
        resolve("/organization/applied/business/suggested/edit/").view_name
        == "charity:edit-suggest-applied-bus"
    )
