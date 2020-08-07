import pytest

from donate_anything.forum.models import Thread
from donate_anything.forum.tests.factories import UserVoteFactory
from donate_anything.item.models import ProposedItem, WantedItem
from donate_anything.item.tests.factories import ItemFactory
from donate_anything.users.tests.factories import UserFactory


pytestmark = pytest.mark.django_db


def setup_thread(thread, entity):
    thread.type = 4
    user = UserFactory.create()
    items = [x.id for x in ItemFactory.create_batch(10)]
    proposed = ProposedItem.objects.create(user_id=user.id, entity=entity, item=items)
    thread.extra = {
        "OP_id": user.id,
        "entity_id": entity.id,
        "proposed_item_id": proposed.id,
    }
    thread.save()


def add_break_even_amount(thread):
    UserVoteFactory.create_batch(4, thread=thread, direction=True)
    UserVoteFactory.create_batch(4, thread=thread, direction=False)
    UserVoteFactory.create(
        thread=thread, direction=True, user=UserFactory.create(is_staff=True)
    )


class TestProposedItemMerge:
    """Tests the merging of ProposedItem for a
    6:10 majority vote including the required 2 staff votes
    with the 2:1 ratio majority on staff side.

    Recall the signal/actual function is only sent on staff command
    The test sets up 10 items to merge. Assume the merge function is error-free.
    """

    def test_complete_merge(self, admin_user, thread, charity):
        setup_thread(thread, charity)
        UserVoteFactory.create_batch(6, thread=thread, direction=True)
        UserVoteFactory.create_batch(4, thread=thread, direction=False)
        UserVoteFactory.create(
            thread=thread, direction=True, user=UserFactory.create(is_staff=True)
        )
        assert WantedItem.objects.count() == 0
        UserVoteFactory.create(thread=thread, direction=True, user=admin_user)
        assert WantedItem.objects.count() == 10
        assert ProposedItem.objects.count() == 1
        assert ProposedItem.objects.first().closed is True

    def test_not_enough_staff_votes(self, admin_user, thread, charity):
        setup_thread(thread, charity)
        UserVoteFactory.create_batch(4, thread=thread, direction=True)
        UserVoteFactory.create_batch(4, thread=thread, direction=False)
        UserVoteFactory.create(thread=thread, direction=True, user=admin_user)
        assert WantedItem.objects.count() == 0

    def test_staff_voted_minority(self, admin_user, thread, charity):
        setup_thread(thread, charity)
        UserVoteFactory.create_batch(4, thread=thread, direction=True)
        UserVoteFactory.create_batch(4, thread=thread, direction=False)
        UserVoteFactory.create(
            thread=thread, direction=False, user=UserFactory.create(is_staff=True)
        )
        UserVoteFactory.create(thread=thread, direction=True, user=admin_user)
        assert WantedItem.objects.count() == 0

    def test_not_enough_votes(self, admin_user, thread, charity):
        setup_thread(thread, charity)
        UserVoteFactory.create_batch(3, thread=thread, direction=True)
        UserVoteFactory.create_batch(4, thread=thread, direction=False)
        UserVoteFactory.create(
            thread=thread, direction=True, user=UserFactory.create(is_staff=True)
        )
        UserVoteFactory.create(thread=thread, direction=True, user=admin_user)
        assert WantedItem.objects.count() == 0

    def test_combined_staff_and_user_should_count(self, thread, admin_user, charity):
        """Tests that with combined staff and users, merge should happen
        because we need a minimum of 10 people
        """
        setup_thread(thread, charity)
        add_break_even_amount(thread)
        UserVoteFactory.create(thread=thread, direction=True, user=admin_user)
        assert WantedItem.objects.count() == 10

    def test_regular_voted_minority(self, admin_user, thread, charity):
        setup_thread(thread, charity)
        UserVoteFactory.create_batch(3, thread=thread, direction=True)
        UserVoteFactory.create_batch(5, thread=thread, direction=False)
        UserVoteFactory.create(
            thread=thread, direction=True, user=UserFactory.create(is_staff=True)
        )
        UserVoteFactory.create(thread=thread, direction=True, user=admin_user)
        assert WantedItem.objects.count() == 0

    def test_signal_only_sent_on_staff_vote(self, user, thread, charity):
        """Tests that the signal is only sent on staff vote to avoid DoS.
        This test acts like the vote should win but a staff member
        didn't vote, so the signal doesn't count.
        """
        setup_thread(thread, charity)
        add_break_even_amount(thread)
        UserVoteFactory.create(thread=thread, direction=True, user=user)
        assert WantedItem.objects.count() == 0

    def test_charity_does_not_exist(self, admin_user, thread, charity):
        setup_thread(thread, charity)
        add_break_even_amount(thread)
        thread = Thread.objects.get(id=thread.id)
        thread.extra["entity_id"] = thread.id + 12345678765432
        thread.save(update_fields=["extra"])
        UserVoteFactory.create(thread=thread, direction=True, user=admin_user)
        assert WantedItem.objects.count() == 0

    def test_proposed_item_does_not_exist(self, admin_user, thread, charity):
        setup_thread(thread, charity)
        add_break_even_amount(thread)
        thread = Thread.objects.get(id=thread.id)
        thread.extra["proposed_item_id"] = thread.id + 12345678765432
        thread.save(update_fields=["extra"])
        UserVoteFactory.create(thread=thread, direction=True, user=admin_user)
        assert WantedItem.objects.count() == 0
