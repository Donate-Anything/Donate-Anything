import pytest
from django.urls import reverse

from donate_anything.forum.models import Thread


pytestmark = pytest.mark.django_db


class TestForumView:
    def test_landing_page(self, client):
        response = client.get(reverse("forum:home"))
        assert response.status_code == 200

    def test_increment_thread_view_count(self, thread, client):
        current_view_count = thread.views
        response = client.get(reverse("forum:thread", kwargs={"thread": thread.id}))
        assert response.status_code == 200
        obj = Thread.objects.get(id=thread.id)
        assert obj.views == current_view_count + 1
