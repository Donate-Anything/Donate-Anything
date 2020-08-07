import logging

from django.db.models.signals import post_save

from donate_anything.forum.models.vote import UserVote
from donate_anything.forum.utils.merge.item import merge_proposed_items


logger = logging.getLogger(__name__)


def merge_on_vote(instance: UserVote, **kwargs):
    """Merges certain objects on vote:
    The objects that can be merged:
    - ProposedItem objects (+ 2 staff)
    """
    if instance.thread.type == 4:
        # ProposedItem voting
        merge_proposed_items(instance)


post_save.connect(merge_on_vote, sender=UserVote)
