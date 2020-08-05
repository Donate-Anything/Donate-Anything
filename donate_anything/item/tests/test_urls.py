import pytest
from django.urls import resolve, reverse

from donate_anything.item.models import ProposedItem


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


def test_list_item_template(charity):
    assert (
        reverse("item:list-item-template", kwargs={"entity_id": charity.id})
        == f"/item/list/{charity.id}/"
    )
    assert resolve(f"/item/list/{charity.id}/").view_name == "item:list-item-template"


def test_list_item_api(charity):
    assert (
        reverse("item:list-item", kwargs={"charity_id": charity.id})
        == f"/item/api/v1/list/{charity.id}/"
    )
    assert resolve(f"/item/api/v1/list/{charity.id}/").view_name == "item:list-item"


def test_list_proposed_item_template(charity, user):
    proposed = ProposedItem.objects.create(entity=charity, user=user)
    assert (
        reverse("item:list-proposed-template", kwargs={"proposed_item_pk": proposed.id})
        == f"/item/list/proposed/{proposed.id}/"
    )
    assert (
        resolve(f"/item/list/proposed/{proposed.id}/").view_name
        == "item:list-proposed-template"
    )


def test_list_proposed_existing_item_api(charity, user):
    proposed = ProposedItem.objects.create(entity=charity, user=user)
    assert (
        reverse("item:list-proposed-item", kwargs={"proposed_item_pk": proposed.id})
        == f"/item/api/v1/proposed/{proposed.id}/exist/"
    )
    assert (
        resolve(f"/item/api/v1/proposed/{proposed.id}/exist/").view_name
        == "item:list-proposed-item"
    )


def test_initial_proposed_template_view():
    assert reverse("item:initial-proposed-template") == "/item/proposed/initial/"
    assert (
        resolve("/item/proposed/initial/").view_name == "item:initial-proposed-template"
    )


def test_list_proposed_item_form():
    assert reverse("item:proposed-item-form") == "/item/proposed/form/"
    assert resolve("/item/proposed/form/").view_name == "item:proposed-item-form"
