import pytest
from django.urls import resolve, reverse


pytestmark = pytest.mark.django_db


def test_organization_view(charity):
    assert (
        reverse("charity:organization", kwargs={"pk": charity.id})
        == f"/organization/{charity.id}/"
    )
    assert resolve(f"/organization/{charity.id}/").view_name == "charity:organization"
