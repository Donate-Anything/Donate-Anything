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


def test_thread_vote_view(thread):
    assert (
        reverse("forum:thread-vote", kwargs={"thread_id": thread.id, "vote_dir": 1})
        == f"/forum/{thread.id}/vote/1/"
    )
    assert resolve(f"/forum/{thread.id}/vote/1/").view_name == "forum:thread-vote"
