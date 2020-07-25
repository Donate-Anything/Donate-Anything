import pytest
from django.http import Http404

from donate_anything.charity.views.list import organization


pytestmark = pytest.mark.django_db


class TestOrganizationView:
    def test_organization_view_success(self, charity, client):
        response = client.get(f"/organization/{charity.id}/")
        assert response.status_code == 200
        assert response.context["name"] == charity.name
        assert response.context["description"] == charity.description
        assert response.context["how_to_donate"] == charity.how_to_donate

    def test_organization_view_not_found(self, rf):
        fake_id = 1
        request = rf.get(f"/organization/{fake_id}")
        with pytest.raises(Http404):
            organization(request, fake_id)
