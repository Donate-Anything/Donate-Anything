import json
from random import choice

import pytest
from django.http.response import Http404

from donate_anything.item.tests.factories import (
    CATEGORY_TYPES,
    CategoryFactory,
    ItemFactory,
    WantedItem,
    WantedItemFactory,
)
from donate_anything.item.views import (
    search_category,
    search_item,
    search_item_autocomplete,
    search_multiple_items,
)


pytestmark = pytest.mark.django_db


class TestItemAutocompleteView:
    def test_typeahead(self, rf):
        query = "an"
        ItemFactory.create(name="pan")
        ItemFactory.create(name="canned food")
        ItemFactory.create(name="blah")
        request = rf.get("item/api/v1/item-autocomplete/", {"q": query})
        response = search_item_autocomplete(request)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data["data"]) == 2, f"Response {data}"
        assert query in data["data"][0][1]
        assert query in data["data"][1][1]

    def test_dissimilar_item_names(self, rf):
        query = "chair"
        ItemFactory.create(name="blah blah")  # DONATABLE BTW
        target = ItemFactory.create(name=query)
        request = rf.get("item/api/v1/item-autocomplete/", {"q": query})
        response = search_item_autocomplete(request)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data["data"]) == 1, f"Response {data}"
        assert data["data"][0] == [target.id, target.name, target.image]

    def test_404_on_empty_query(self, rf):
        request = rf.get("item/api/v1/item-autocomplete/")
        with pytest.raises(Http404):
            search_item_autocomplete(request)

    def test_show_only_appropriate(self, rf):
        # Remember, "name" is unique.
        ItemFactory.create(name="chai", is_appropriate=False)
        ItemFactory.create(name="hair", is_appropriate=False)  # DONATABLE BTW
        target = ItemFactory.create(name="chair", is_appropriate=True)
        request = rf.get("item/api/v1/item-autocomplete/", {"q": "chair"})
        response = search_item_autocomplete(request)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data["data"]) == 1
        assert data["data"][0] == [target.id, target.name, target.image]


def _assert_org_list_eq(response_data, inputted_data):
    data = sorted(response_data, key=lambda x: x[0])
    orgs = sorted(
        [[x.charity.id, x.charity.name, x.charity.description] for x in inputted_data],
        key=lambda x: x[0],
    )
    for x, y in zip(data, orgs):
        assert x == y


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
        request = rf.get(f"item/lookup/{item.id}")
        response = search_item(request, item.id)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data["data"]) == 3
        _assert_org_list_eq(data["data"], wanted_items)


class TestSearchMultipleItems:
    def test_search_multiple_items(self, client, charity):
        # Create the items
        chair = ItemFactory.create(name="chair")
        pan = ItemFactory.create(name="pan")
        jeans = ItemFactory.create(name="jeans")
        # Create items organizations wants
        WantedItemFactory.create_batch(3, item=chair)  # 3
        WantedItemFactory.create(item=chair, charity=charity)  # 4
        WantedItemFactory.create(item=pan, charity=charity)  # 4 since same charity
        WantedItemFactory.create_batch(2, item=pan)  # 6
        WantedItemFactory.create(item=jeans)  # 7

        WantedItemFactory.create_batch(25, item=jeans)

        response = client.get(
            f"/item/multi-lookup/?q={chair.id}&&q={pan.id}&&q={jeans.id}"
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

    def test_search_multiple_items_with_page(self, rf):
        request = rf.get(f"item/multi-lookup/", {"q": 1, "page": str(1)})
        response = search_multiple_items(request)
        assert response.status_code == 200

    def test_invalid_search_multiple_item_input(self, rf):
        request = rf.get(f"item/multi-lookup/", {"page": "string"})
        with pytest.raises(Http404):
            search_multiple_items(request)
