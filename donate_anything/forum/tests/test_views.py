import pytest
from django.urls import reverse


pytestmark = pytest.mark.django_db


class TestForumView:
    def test_landing_page(self, client, user):
        client.force_login(user)
        response = client.get(reverse("forum:home"))
        assert response.status_code == 200
