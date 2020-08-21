from typing import List

from django.utils.html import escape

from donate_anything.charity.models import Charity
from donate_anything.item.models import Item, ProposedItem, WantedItem


def merge(entity: Charity, proposed: ProposedItem):
    """Merges a user's proposed items to an active
    entity's actual list of supported items.

    What happens when a duplicate like this appears regarding condition?
    First or second? First :)
    """
    # FIXME merging items is wayyyyy too inefficient. Python binding for C?
    # 1. create the new items that already exist in Item
    # This is necessary in case item.id doesn't exist
    # so we remove the non-existent items via intersection.
    _items_obj_from_item_array = Item.objects.filter(id__in=proposed.item).values_list(
        "id", flat=True
    )
    _proposed_items: List[int] = proposed.item.copy()
    for item_id in _proposed_items:
        if item_id not in _items_obj_from_item_array:
            indices = (i for i, x in enumerate(proposed.item) if x == item_id)
            # Remove this nonexistent item
            for index in indices:
                del proposed.item[index]
                del proposed.item_condition[index]
    _proposed_items: List[int] = proposed.item.copy()
    del _proposed_items
    WantedItem.objects.bulk_create(
        [
            WantedItem(item_id=x, condition=c, charity=entity)
            for x, c in zip(proposed.item, proposed.item_condition)
        ],
        ignore_conflicts=True,
    )
    # All ignoring_conflicts is in case of UniqueConstraint
    # but this means no duplicates are created.
    # It also won't affect future work since proposed.item is never accessed again
    # Ref: test_selected_existing_already_in_active_item

    # 2. Check for any existing items in "proposed new items"
    # Can happen when a new item shows up due to a different merge
    # but it didn't update the array here to reflect the new item
    # (i.e. the "name" was not moved to an integer ID in "item" attr).
    try:
        proposed_names: List[str] = list(
            escape(x).lower().replace(",", "") for x in proposed.names
        )
    except TypeError:
        proposed_names = []
    existing_name_item_objs = Item.objects.filter(name__in=proposed_names)
    existing_name_item_conditions: List[int] = []
    for item in existing_name_item_objs:
        indices = (i for i, x in enumerate(proposed_names) if x == item.name)
        for index in indices:
            existing_name_item_conditions.append(proposed.names_condition[index])
            # Remove since in the future, we're creating new items based on proposed_names
            del proposed_names[index]
            del proposed.names_condition[index]
    # This is ok to be ignore_conflicts since we're only violating unique constraint
    # so ignoring conflicts here means don't create
    WantedItem.objects.bulk_create(
        [
            WantedItem(item=item, condition=c, charity=entity)
            for item, c in zip(existing_name_item_objs, existing_name_item_conditions)
        ],
        ignore_conflicts=True,
    )

    # 3. Finally create the rest of the items that are not in the Item table.
    try:
        # Set.difference returns only elements from 1st set that aren't in second.
        _names = (x.name for x in existing_name_item_objs)
        _non_existing_names = [name for name in proposed_names if name not in _names]
        del _names
        if not _non_existing_names:
            raise AttributeError
        # Remove duplicates from non_existing_names
        non_existing_names = []
        non_existing_conditions = []
        for i, name in enumerate(_non_existing_names):
            if name not in non_existing_names:
                non_existing_names.append(name)
                non_existing_conditions.append(proposed.names_condition[i])
        del _non_existing_names

        # Because we're using PostgreSQL, we get the pks from bulk_create
        items = Item.objects.bulk_create([Item(name=x) for x in non_existing_names])
        WantedItem.objects.bulk_create(
            [
                WantedItem(item=item, condition=c, charity=entity)
                for item, c in zip(items, non_existing_conditions)
            ],
            ignore_conflicts=True,
        )
    except AttributeError:
        # In case proposed_names is empty... although I guess we should've handled this beforehand...
        pass

    proposed.closed = True
    proposed.save(update_fields=["closed"])
