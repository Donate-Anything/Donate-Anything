import logging

from donate_anything.charity.models import Charity
from donate_anything.forum.models.vote import UserVote
from donate_anything.item.models import ProposedItem
from donate_anything.item.utils.merge_proposed_to_active import merge


logger = logging.getLogger(__name__)


def merge_proposed_items(instance: UserVote):
    """ProposedItem voting
    Requires at least two staff members' approval (early stage)
    that aren't counted in the majority
    and 60% regular majority for approval. Only superusers can override
    (early stage since our mods/staff can't be trusted too early).
    10 people is the minimum, staff inclusive.
    """
    if instance.user.is_staff and instance.direction is True:
        thread = instance.thread
        staff_votes = UserVote.objects.select_related("user").filter(
            thread_id=thread.id, user__is_staff=True
        )
        staff_upvotes = len([0 for x in staff_votes if x.direction is True])
        staff_downvotes = len([0 for x in staff_votes if x.direction is False])
        # Add to avoid zero division
        if (
            staff_upvotes / (staff_upvotes + staff_downvotes) >= 2 / 3
            and len(staff_votes) >= 2
        ):
            upvotes = UserVote.objects.filter(
                thread_id=thread.id, direction=True
            ).count()
            downvotes = UserVote.objects.filter(
                thread_id=thread.id, direction=False
            ).count()
            if upvotes + downvotes < 10:
                return
            if upvotes / (upvotes + downvotes) >= 0.6:
                try:
                    proposed = ProposedItem.objects.get(
                        id=thread.extra["proposed_item_id"]
                    )
                    merge(
                        Charity.objects.get(id=thread.extra["entity_id"]),
                        proposed,
                    )
                    ProposedItem.objects.filter(id=proposed.id).update(closed=True)
                except (ProposedItem.DoesNotExist, Charity.DoesNotExist):
                    logger.error(
                        f"Merge failed for ProposedItem "
                        f"{thread.extra['proposed_item_id']} for Entity "
                        f"{thread.extra['entity_id']}"
                    )
