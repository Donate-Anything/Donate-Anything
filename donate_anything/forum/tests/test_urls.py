import pytest
from django.urls import resolve, reverse


pytestmark = pytest.mark.django_db


def test_forum_view():
    assert reverse("forum:home") == "/forum/"
    assert resolve("/forum/").view_name == "forum:home"


def test_thread_view(thread):
    assert (
        reverse("forum:thread", kwargs={"thread": thread.id}) == f"/forum/{thread.id}/"
    )
    assert resolve(f"/forum/{thread.id}/").view_name == "forum:thread"
