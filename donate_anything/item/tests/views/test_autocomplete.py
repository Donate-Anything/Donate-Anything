import json

import pytest
from django.http.response import Http404

from donate_anything.item.models.item import WANTED_ITEM_CONDITIONS
from donate_anything.item.tests.factories import ItemFactory
from donate_anything.item.views import search_item_autocomplete


pytestmark = pytest.mark.django_db
_wanted_items_condition_ids = [x[0] for x in WANTED_ITEM_CONDITIONS]


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

    def test_return_closest_exact_matching(self, rf):
        """Tests closest matching in terms of number of letters
        close to the query. "Three-ring binder shows up before
        binder...
        """
        target1 = ItemFactory.create(name="three-ring binder")
        target2 = ItemFactory.create(name="binder")
        request = rf.get("blah/", {"q": "binder"})
        response = search_item_autocomplete(request)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data["data"]) == 2
        assert data["data"][0] == [target2.id, target2.name, target2.image]
        assert data["data"][1] == [target1.id, target1.name, target1.image]
