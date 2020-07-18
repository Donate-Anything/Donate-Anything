import pytest
from django.urls import resolve, reverse


pytestmark = pytest.mark.django_db


def test_search_item_autocomplete():
    assert reverse("item:item-autocomplete") == "/item/api/v1/item-autocomplete/"
    assert (
        resolve("/item/api/v1/item-autocomplete/").view_name == "item:item-autocomplete"
    )


def test_search_category():
    category_type = 1
    assert (
        reverse("item:category-filter", kwargs={"category_type": category_type})
        == f"/item/api/v1/category/{category_type}/"
    )
    assert (
        resolve(f"/item/api/v1/category/{category_type}/").view_name
        == "item:category-filter"
    )


def test_search_item(item):
    assert (
        reverse("item:lookup-item", kwargs={"pk": item.id})
        == f"/item/lookup/{item.id}/"
    )
    assert resolve(f"/item/lookup/{item.id}/").view_name == "item:lookup-item"


def test_search_multiple_items():
    assert reverse("item:lookup-multi-item") == "/item/multi-lookup/"
    assert resolve("/item/multi-lookup/").view_name == "item:lookup-multi-item"
