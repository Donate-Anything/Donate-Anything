from django.utils.html import escape

from donate_anything.charity.models import Charity
from donate_anything.item.models import Item, ProposedItem, WantedItem


def merge(entity: Charity, proposed: ProposedItem):
    """Merges a user's proposed items to an active
    entity's actual list of supported items.
    """
    # First create the new items that already exist in Item
    # This is necessary in case item.id doesn't exist
    proposed.item = set(proposed.item).intersection(
        Item.objects.only("id")
        .filter(id__in=proposed.item)
        .values_list("id", flat=True)
    )
    WantedItem.objects.bulk_create(
        [WantedItem(item_id=x, charity=entity) for x in proposed.item],
        ignore_conflicts=True,
    )
    # All ignoring_conflicts is in case of UniqueConstraint

    # Check for any existing items in "proposed new items"
    # Can happen when a new item shows up from a different merge but didn't update the array here
    try:
        proposed_names = {escape(x).lower() for x in proposed.names}
    except TypeError:
        proposed_names = set()
    existing_name_item_objs = Item.objects.filter(name__in=proposed_names)
    # This is ok to be ignore_conflicts since we're only violating unique constraint
    # so ignoring conflicts here means don't create
    WantedItem.objects.bulk_create(
        [WantedItem(item=item, charity=entity) for item in existing_name_item_objs],
        ignore_conflicts=True,
    )

    # Finally create the rest of the items
    try:
        # Set.difference returns only elements from 1st set that aren't in second.
        non_existing_names = proposed_names.difference(
            {x.name for x in existing_name_item_objs}
        )
        # Because we're using PostgreSQL, we get the pks from bulk_create
        items = Item.objects.bulk_create([Item(name=x) for x in non_existing_names])
        WantedItem.objects.bulk_create(
            [WantedItem(item=item, charity=entity) for item in items],
            ignore_conflicts=True,
        )
    except AttributeError:
        # In case proposed_names is empty... although I guess we should've handled this beforehand.....
        pass

    proposed.closed = True
    proposed.save(update_fields=["closed"])
