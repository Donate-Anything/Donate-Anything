import json
from random import choice

import pytest
from django.contrib.auth.models import AnonymousUser
from django.http.response import Http404

from donate_anything.item.models.item import WANTED_ITEM_CONDITIONS
from donate_anything.item.tests.factories import (
    CATEGORY_TYPES,
    CategoryFactory,
    ItemFactory,
    WantedItem,
    WantedItemFactory,
)
from donate_anything.item.utils.base_converter import item_encode_b64
from donate_anything.item.views import (
    item_children,
    search_category,
    search_item,
    search_multiple_items,
)


pytestmark = pytest.mark.django_db
_wanted_items_condition_ids = [x[0] for x in WANTED_ITEM_CONDITIONS]


class TestItemInformation:
    # Doesn't include parent since we assume it's already known
    def test_get_item_children_authenticated_only(self, rf):
        request = rf.get("blah/")
        request.user = AnonymousUser()
        with pytest.raises(Http404):
            item_children(request, 1)

    def test_children_level_1(self, rf, user):
        parent = ItemFactory.create()
        progeny = ItemFactory.create_batch(9, parent=parent)
        request = rf.get("blah/")
        request.user = user
        response = item_children(request, parent.id)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data["data"]) == 9
        assert sorted(data["data"], key=lambda x: x[0]) == [
            [x.id, x.name] for x in progeny
        ]

    def test_no_children(self, rf, user):
        parent = ItemFactory.create()
        progeny = ItemFactory.create_batch(9, parent=parent)
        request = rf.get("blah/")
        request.user = user
        response = item_children(request, progeny[0].id)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data["data"]) == 0
        assert data["data"] == []

    def test_children_multi_level(self, rf, user):
        item1 = ItemFactory.create()
        item2a = ItemFactory.create(parent=item1)
        item3a = ItemFactory.create_batch(3, parent=item2a)
        item2b = ItemFactory.create(parent=item1)
        item3b = ItemFactory.create_batch(6, parent=item2b)
        request = rf.get("blah/")
        request.user = user
        response = item_children(request, item1.id)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data["data"]) == 11
        assert sorted(data["data"], key=lambda x: x[0]) == [
            [x.id, x.name]
            for x in sorted((item2a, item2b, *item3a, *item3b), key=lambda x: x.id)
        ]

    def test_recursion(self, rf, user):
        item1 = ItemFactory.create()
        item2 = ItemFactory.create(parent=item1)
        item1.parent = item2
        item1.save(update_fields=["parent"])
        request = rf.get("blah/")
        request.user = user
        response = item_children(request, item1.id)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data["data"]) == 1
        assert sorted(data["data"], key=lambda x: x[0]) == [[item2.id, item2.name]]


def _assert_org_list_eq(response_data, inputted_data):
    data = sorted(response_data, key=lambda x: x[0])
    orgs = sorted(
        [[x.charity.id, x.charity.name, x.charity.description] for x in inputted_data],
        key=lambda x: x[0],
    )
    for x, y in zip(data, orgs):
        assert x == y


def _item_test_request(rf, encoded, wanted_items):
    request = rf.get(f"item/lookup/{encoded}")
    response = search_item(request, encoded)
    assert response.status_code == 200
    data = json.loads(response.content)
    assert len(data["data"]) == 3
    _assert_org_list_eq(data["data"], wanted_items)


class TestPaginateViaCharity:
    """Tests the protected func that paginates organizations.
    Every view that utilizes this is tested here, except for multi-lookup.
    """

    def test_filter_by_category(self, rf):
        category_type = CATEGORY_TYPES[0][0]
        # Created a random category just to make sure it wasn't jumbled in
        CategoryFactory.create(category=category_type + 1)
        categories = CategoryFactory.create_batch(3, category=category_type)
        request = rf.get(f"item/api/v1/category/{category_type}/")
        response = search_category(request, category_type)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data["data"]) == 3
        # Make sure the data is correct.
        _assert_org_list_eq(data["data"], categories)

    def test_filter_category_search_by_page(self, rf):
        """Test pagination of category filtering
        """
        category_type = choice(CATEGORY_TYPES)[0]
        # Test the second page
        CategoryFactory.create_batch(26, category=category_type)
        request = rf.get(f"item/api/v1/category/{category_type}/", {"page": 2})
        response = search_category(request, category_type)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert (
            len(data["data"]) == 1
        ), "The paginator should show only 1 organization since page size is 25."

    @pytest.mark.parametrize("category_type", [-1, len(CATEGORY_TYPES)])
    def test_error_on_invalid_category_type(self, rf, category_type):
        request = rf.get(f"item/api/v1/category/{category_type}/")
        # Error on 404 since typical user shouldn't really get this path.
        with pytest.raises(Http404):
            search_category(request, category_type)

    def test_search_item(self, rf, item):
        wanted_items = WantedItemFactory.create_batch(3, item=item)
        encoded = item_encode_b64(item.id)
        _item_test_request(rf, encoded, wanted_items)

    @pytest.mark.parametrize("num", [x for x in range(10)])
    def test_search_item_single_digit_bad(self, rf, num):
        request = rf.get(f"item/lookup/{num}")
        response = search_item(request, str(num))
        assert response.status_code == 400

    def test_search_item_show_if_condition_is_better_than_wanted_item(self, rf, item):
        condition = 2
        wanted_items = WantedItemFactory.create_batch(3, item=item, condition=condition)
        encoded = item_encode_b64(item.id, condition + 1)
        _item_test_request(rf, encoded, wanted_items)

    def test_search_item_dont_show_if_not_condition_well_enough(self, rf, item):
        """Searching an item of brand new will show up for all organizations.
        If you have a poor condition item, then only show WantedItem with 0
        and below (which is none since 0 is the lowest).
        """
        condition = 2
        WantedItemFactory.create_batch(3, item=item, condition=condition)
        encoded = item_encode_b64(item.id, condition - 1)
        request = rf.get(f"item/lookup/{encoded}")
        response = search_item(request, encoded)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data["data"]) == 0


class TestSearchMultipleItems:
    def test_search_multiple_items(self, client, charity):
        # Create the items
        chair = ItemFactory.create(name="chair")
        pan = ItemFactory.create(name="pan")
        jeans = ItemFactory.create(name="jeans")
        # Create items organizations wants
        # All items are created with condition 3: Brand New
        WantedItemFactory.create_batch(3, item=chair)  # 3
        WantedItemFactory.create(item=chair, charity=charity)  # 4
        WantedItemFactory.create(item=pan, charity=charity)  # 4 since same charity
        WantedItemFactory.create_batch(2, item=pan)  # 6
        WantedItemFactory.create(item=jeans)  # 7

        WantedItemFactory.create_batch(25, item=jeans)

        response = client.get(
            f"/item/multi-lookup/?"
            f"q={item_encode_b64(chair.id, 3)}&"
            f"q={item_encode_b64(pan.id, 3)}&"
            f"q={item_encode_b64(jeans.id, 3)}"
        )
        assert response.status_code == 200
        data: dict = response.context["data"]
        assert len(data) == 25, f"Supposed to show 25 max pagination.\n{data}"
        assert response.context["page_obj"].has_next() is True
        assert response.context["page_obj"].has_previous() is False
        first_key = list(data.keys())[0]
        assert first_key == charity.id, (
            "Target charity, which supports the most items "
            "out of the searched, should be the first result."
        )
        assert (
            len(data[first_key][:-2])
            == WantedItem.objects.filter(
                item_id__in=[chair.id, pan.id, jeans.id], charity=charity,
            ).count()
        ), (
            "Assuming the additional information is only name and description"
            "of the organization, hence -2 in the test, then you're missing items."
        )

        charities_seen = []
        for k in data.keys():
            # Check the rest isn't the exact same charity
            assert k not in charities_seen, "Charities shown must be distinct"
            charities_seen.append(k)
            # Check the necessary information is there: name, description

    def test_multiple_conditions(self):
        """Ref these two tests which explains this one (it's a combo of both):
        test_search_item_show_if_condition_is_better_than_wanted_item
        test_search_item_dont_show_if_not_condition_well_enough
        """

    @pytest.mark.parametrize("condition", _wanted_items_condition_ids)
    def test_search_multi_better_condition(self, client, charity, condition):
        """Only filter by item of searched conditions(s) or better
        """

    def test_search_multiple_items_with_page(self, rf):
        request = rf.get(f"item/multi-lookup/", {"q": item_encode_b64(1), "page": "1"})
        response = search_multiple_items(request)
        assert response.status_code == 200

    @pytest.mark.parametrize("q", [x for x in range(10)])
    def test_search_cannot_use_digits(self, rf, q):
        """Using digits in q query parameter is not allowed since
        our decoding formula reserves that no single digits can be made
        an input (due to the item id + condition).
        """
        request = rf.get(f"item/multi-lookup/", {"q": str(q), "page": "1"})
        response = search_multiple_items(request)
        assert response.status_code == 400

    def test_invalid_search_multiple_item_input(self, rf):
        request = rf.get(f"item/multi-lookup/", {"page": "string"})
        with pytest.raises(Http404):
            search_multiple_items(request)
