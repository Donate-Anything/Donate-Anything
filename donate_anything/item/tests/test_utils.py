from random import sample
from string import ascii_letters

import pytest

from donate_anything.item.models import Item, ProposedItem, WantedItem
from donate_anything.item.tests.factories import ItemFactory
from donate_anything.item.utils.merge_proposed_to_active import merge


pytestmark = pytest.mark.django_db


class TestMergeProposedItemToActive:
    def test_merge(self, charity, user):
        # Assuming names attribute are of names that aren't in Item list already.
        items = ItemFactory.create_batch(10)
        names = [("".join(sample(ascii_letters, 50))).lower() for _ in range(10)]
        proposed = ProposedItem.objects.create(
            entity=charity, user=user, item=[item.id for item in items], names=names
        )
        assert ProposedItem.objects.get(id=proposed.id).closed is False
        merge(charity, proposed)
        assert Item.objects.count() == 20, "Names list should've created 10 Item objs"
        for x in names:
            assert Item.objects.filter(name=x).exists()
        assert WantedItem.objects.filter(charity=charity).count() == 20
        assert ProposedItem.objects.get(id=proposed.id).closed is True

    def test_selected_existing_already_in_active_item(self, charity, user):
        """Tests no new WantedItems are created if the item
        is already in WantedItem for the entity.
        """
        items = ItemFactory.create_batch(11)
        WantedItem.objects.bulk_create(
            [WantedItem(charity=charity, item=item) for item in items]
        )
        assert WantedItem.objects.count() == 11
        # Add lingering Item that isn't a part of entity yet
        random_item = ItemFactory.create()
        items.append(random_item)
        # Create proposed item
        proposed = ProposedItem.objects.create(
            entity=charity, user=user, item=[item.id for item in items],
        )
        merge(charity, proposed)
        assert WantedItem.objects.count() == 12, "Only one item should've been added"
        assert WantedItem.objects.filter(charity=charity, item=random_item).exists()

    def test_non_existing_already_in_active_item(self, charity, user):
        """Tests if an item that exists in Item but user thought
        it didn't (so it's in the names list) will NOT create a new
        Item object but use the existing one to create the WantedItem.
        """
        items = ItemFactory.create_batch(9)
        assert Item.objects.count() == 9
        WantedItem.objects.bulk_create(
            [WantedItem(charity=charity, item=item) for item in items]
        )
        proposed = ProposedItem.objects.create(
            entity=charity, user=user, names=[item.name.lower() for item in items]
        )
        merge(charity, proposed)
        assert Item.objects.count() == 9
        assert WantedItem.objects.count() == 9

    def test_non_existing_already_in_item(self, charity, user):
        """Tests if an item that exists in Item but user thought
        it didn't (so it's in the names list) will NOT create a new
        Item object but will create a new WantedItem.
        """
        items = ItemFactory.create_batch(9)
        assert Item.objects.count() == 9
        proposed = ProposedItem.objects.create(
            entity=charity, user=user, names=[item.name.lower() for item in items]
        )
        merge(charity, proposed)
        assert Item.objects.count() == 9
        assert WantedItem.objects.count() == 9

    def test_create_new_item(self, charity, user):
        assert Item.objects.count() == 0
        proposed = ProposedItem.objects.create(
            entity=charity, user=user, names=["hi there"]
        )
        merge(charity, proposed)
        assert Item.objects.count() == 1
        assert Item.objects.first().name == "hi there"
        assert WantedItem.objects.count() == 1

    def test_remove_duplicate_items(self, charity, user):
        item = ItemFactory.create()
        proposed = ProposedItem.objects.create(
            entity=charity, user=user, item=[item.id, item.id],
        )
        merge(charity, proposed)
        assert WantedItem.objects.count() == 1

    def test_remove_duplicate_names(self, charity, user):
        random_string = ("".join(sample(ascii_letters, 10))).lower()
        proposed = ProposedItem.objects.create(
            entity=charity, user=user, names=[random_string, random_string]
        )
        merge(charity, proposed)
        assert Item.objects.count() == 1
        assert WantedItem.objects.count() == 1

    def test_duplicate_name_and_item(self, charity, user):
        """Tests that a duplicate listed name and listed item
        don't create two WantedItems.
        """
        item = ItemFactory.create()
        proposed = ProposedItem.objects.create(
            entity=charity, user=user, item=[item.id], names=[item.name.lower()]
        )
        merge(charity, proposed)
        assert Item.objects.count() == 1
        assert WantedItem.objects.count() == 1
        assert WantedItem.objects.filter(charity=charity)[0].item == item

    def test_escape(self, charity, user):
        proposed = ProposedItem.objects.create(
            entity=charity, user=user, names=["<p>hi</p>"]
        )
        merge(charity, proposed)
        assert Item.objects.count() == 1
        assert WantedItem.objects.count() == 1
        assert WantedItem.objects.first().item.name == "&lt;p&gt;hi&lt;/p&gt;"
