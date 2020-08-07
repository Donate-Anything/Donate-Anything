from typing import List

import pytest
from django.urls import reverse

from donate_anything.forum.models import Thread, UserVote
from donate_anything.forum.models.forum import THREAD_TYPE_CHOICES, VOTABLE_THREADS


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


def not_votable_threads() -> List[int]:
    thread_types = [x[0] for x in THREAD_TYPE_CHOICES]
    return list(set(thread_types).difference(VOTABLE_THREADS))


class TestVote:
    @pytest.mark.parametrize("thread_type", [x[0] for x in THREAD_TYPE_CHOICES])
    def test_can_vote_certain_thread_type(self, client, thread, thread_type, user):
        Thread.objects.filter(id=thread.id).update(type=thread_type)
        votable = thread_type in VOTABLE_THREADS
        client.force_login(user)
        response = client.post(
            reverse("forum:thread-vote", kwargs={"thread_id": thread.id, "vote_dir": 1})
        )
        if votable:
            assert response.status_code == 200
            assert UserVote.objects.count() == 1
        else:
            assert response.status_code == 403
            assert UserVote.objects.count() == 0

    def test_thread_doesnt_exist(self, client, user):
        client.force_login(user)
        response = client.post(
            reverse("forum:thread-vote", kwargs={"thread_id": 1, "vote_dir": 1})
        )
        assert response.status_code == 404
        assert UserVote.objects.count() == 0

    def test_cant_vote_if_thread_accepted(self, client, user, thread):
        Thread.objects.filter(id=thread.id).update(
            type=VOTABLE_THREADS[0], accepted=True
        )
        client.force_login(user)
        response = client.post(
            reverse("forum:thread-vote", kwargs={"thread_id": thread.id, "vote_dir": 1})
        )
        assert response.status_code == 403

    def test_thread_accepted_and_not_votable(self, client, thread, user):
        Thread.objects.filter(id=thread.id).update(
            accepted=True, type=not_votable_threads()[0]
        )
        client.force_login(user)
        assert UserVote.objects.count() == 0
        response = client.post(
            reverse("forum:thread-vote", kwargs={"thread_id": thread.id, "vote_dir": 1})
        )
        assert response.status_code == 403
        assert UserVote.objects.count() == 0

    @pytest.mark.parametrize(
        "old_vote,new_vote", [(0, 1), (1, 0), (1, 1234), (1234, 1)]
    )
    def test_update_vote(self, client, user, thread, old_vote, new_vote):
        Thread.objects.filter(id=thread.id).update(type=VOTABLE_THREADS[0])
        vote = UserVote.objects.create(
            user=user, direction=(True if old_vote == 1 else False), thread=thread
        )
        assert vote.direction is (True if old_vote == 1 else False)
        client.force_login(user)
        response = client.post(
            reverse(
                "forum:thread-vote",
                kwargs={"thread_id": thread.id, "vote_dir": new_vote},
            )
        )
        assert response.status_code == 200
        assert UserVote.objects.count() == 1
        obj = UserVote.objects.get(id=vote.id)
        assert obj.direction is (True if new_vote == 1 else False)
        assert obj.thread == thread
