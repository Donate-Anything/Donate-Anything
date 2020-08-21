from random import randint, sample
from string import ascii_letters

import pytest

from donate_anything.item.models import Item, ProposedItem, WantedItem
from donate_anything.item.tests.factories import ItemFactory
from donate_anything.item.utils.base_converter import (
    b64_to_wanted_item,
    item_encode_b64,
)
from donate_anything.item.utils.merge_proposed_to_active import merge


pytestmark = pytest.mark.django_db


class TestMergeProposedItemToActive:
    def test_merge(self, charity, user):
        # Assuming names attribute are of names that aren't in Item list already.
        items = ItemFactory.create_batch(10)
        item_conditions = [randint(0, 3) for _ in range(len(items))]
        names = [("".join(sample(ascii_letters, 50))).lower() for _ in range(10)]
        names_condition = [randint(0, 3) for _ in range(len(names))]
        proposed = ProposedItem.objects.create(
            entity=charity,
            user=user,
            item=[item.id for item in items],
            item_condition=item_conditions,
            names=names,
            names_condition=names_condition,
        )
        assert ProposedItem.objects.get(id=proposed.id).closed is False
        merge(charity, proposed)
        assert Item.objects.count() == 20, "Names list should've created 10 Item objs"
        for x in names:
            assert Item.objects.filter(name=x).exists()
        assert WantedItem.objects.filter(charity=charity).count() == 20
        for item, condition in zip(items, item_conditions):
            assert WantedItem.objects.filter(
                item=item, condition=condition, charity=charity
            ).exists()
        for name, condition in zip(names, names_condition):
            assert WantedItem.objects.filter(
                item__name=name, condition=condition, charity=charity
            ).exists()
        assert ProposedItem.objects.get(id=proposed.id).closed is True

    def test_selected_existing_already_in_active_item(self, charity, user):
        """Tests no new WantedItems are created if the item
        is already in WantedItem for the entity.
        """
        items = ItemFactory.create_batch(11)
        items_conditions = [randint(0, 3) for _ in range(len(items))]
        WantedItem.objects.bulk_create(
            [
                WantedItem(charity=charity, item=item, condition=condition)
                for item, condition in zip(items, items_conditions)
            ]
        )
        assert WantedItem.objects.count() == 11
        # Add lingering Item that isn't a part of entity yet
        random_item = ItemFactory.create()
        items.append(random_item)
        items_conditions.append(randint(0, 3))
        # Create proposed item
        proposed = ProposedItem.objects.create(
            entity=charity,
            user=user,
            item=[item.id for item in items],
            item_condition=items_conditions,
        )
        merge(charity, proposed)
        assert WantedItem.objects.count() == 12, "Only one item should've been added"
        assert WantedItem.objects.get(item=random_item)
        assert WantedItem.objects.distinct("item", "charity").count() == 12
        for item, condition in zip(items, items_conditions):
            assert WantedItem.objects.filter(
                item=item, condition=condition, charity=charity
            ).exists()
        assert WantedItem.objects.filter(charity=charity, item=random_item).exists()

    def test_non_existing_already_in_active_item(self, charity, user):
        """Tests if an item that exists in Item but user thought
        it didn't (so it's in the names list) will NOT create a new
        Item object but use the existing one to create the WantedItem.
        """
        items = ItemFactory.create_batch(9)
        assert Item.objects.count() == 9
        item_conditions = [randint(0, 3) for _ in range(len(items))]
        WantedItem.objects.bulk_create(
            [
                WantedItem(charity=charity, item=item, condition=condition)
                for item, condition in zip(items, item_conditions)
            ]
        )
        proposed = ProposedItem.objects.create(
            entity=charity,
            user=user,
            names=[item.name.lower() for item in items],
            # Different conditions
            names_condition=[randint(0, 3) for _ in range(len(items))],
        )
        merge(charity, proposed)
        assert Item.objects.count() == 9
        assert WantedItem.objects.count() == 9
        for item, condition in zip(items, item_conditions):
            assert WantedItem.objects.filter(
                item=item, condition=condition, charity=charity
            ).exists()

    def test_non_existing_already_in_item(self, charity, user):
        """Tests if an item that exists in Item but user thought
        it didn't (so it's in the names list) will NOT create a new
        Item object but will create a new WantedItem.
        """
        items = ItemFactory.create_batch(9)
        assert Item.objects.count() == 9
        names_condition = [randint(0, 3) for _ in range(9)]
        proposed = ProposedItem.objects.create(
            entity=charity,
            user=user,
            names=[item.name.lower() for item in items],
            names_condition=names_condition,
        )
        merge(charity, proposed)
        assert Item.objects.count() == 9
        assert WantedItem.objects.count() == 9
        for name, condition in zip(items, names_condition):
            assert WantedItem.objects.filter(
                item__name=name, condition=condition, charity=charity
            )

    def test_create_new_item(self, charity, user):
        assert Item.objects.count() == 0
        names_condition = randint(0, 3)
        proposed = ProposedItem.objects.create(
            entity=charity,
            user=user,
            names=["hi there"],
            names_condition=[names_condition],
        )
        merge(charity, proposed)
        assert Item.objects.count() == 1
        item = Item.objects.get(name="hi there")
        assert WantedItem.objects.count() == 1
        assert WantedItem.objects.first().condition == names_condition
        assert WantedItem.objects.first().item == item

    def test_remove_duplicate_items(self, charity, user):
        item = ItemFactory.create()
        # What happens when a duplicate like this appears? First or second? First :)
        proposed = ProposedItem.objects.create(
            entity=charity, user=user, item=[item.id, item.id], item_condition=[2, 1]
        )
        merge(charity, proposed)
        assert Item.objects.count() == 1
        assert WantedItem.objects.count() == 1
        assert WantedItem.objects.first().condition == 2

    def test_remove_duplicate_names(self, charity, user):
        random_string = ("".join(sample(ascii_letters, 10))).lower()
        proposed = ProposedItem.objects.create(
            entity=charity,
            user=user,
            names=[random_string, random_string],
            names_condition=[2, 1],
        )
        merge(charity, proposed)
        assert Item.objects.get(name=random_string)
        assert WantedItem.objects.count() == 1
        assert WantedItem.objects.first().condition == 2

    def test_duplicate_name_and_item(self, charity, user):
        """Tests that a duplicate listed name and listed item
        don't create two WantedItems.
        """
        item = ItemFactory.create()
        proposed = ProposedItem.objects.create(
            entity=charity,
            user=user,
            item=[item.id],
            item_condition=[1],
            names=[item.name.lower()],
            names_condition=[2],
        )
        merge(charity, proposed)
        assert Item.objects.get(name=item.name)
        assert WantedItem.objects.count() == 1
        wanted_item = WantedItem.objects.first()
        assert wanted_item.item == item
        assert wanted_item.condition == 1

    def test_escape(self, charity, user):
        proposed = ProposedItem.objects.create(
            entity=charity, user=user, names=["<p>hi,</p>"], names_condition=[2]
        )
        merge(charity, proposed)
        assert Item.objects.count() == 1
        assert WantedItem.objects.count() == 1
        assert WantedItem.objects.first().item.name == "&lt;p&gt;hi&lt;/p&gt;"

    def test_item_not_real_item_so_ignore(self, charity, user):
        proposed = ProposedItem.objects.create(
            entity=charity, user=user, item=[1], item_condition=[2]
        )
        merge(charity, proposed)
        assert Item.objects.count() == 0
        assert WantedItem.objects.count() == 0


_big_serial_max = 9223372036854775807


class TestUrlShortening:
    @pytest.mark.parametrize("item_id", [1, 98345, _big_serial_max])
    def test_encode(self, item_id):
        """Checks the length actually decreased"""
        condition = 2
        assert len(item_encode_b64(item_id, condition)) < len(
            str(item_id) + str(condition)
        )

    @pytest.mark.parametrize("item_id", [0, -1, -232])
    def test_raise_if_item_id_is_less_than_0(self, item_id):
        with pytest.raises(AssertionError):
            item_encode_b64(item_id)

    def test_decode(self):
        b64_to_wanted_item(item_encode_b64(_big_serial_max))

    def test_decode_must_not_be_empty(self):
        with pytest.raises(AssertionError):
            b64_to_wanted_item("")
