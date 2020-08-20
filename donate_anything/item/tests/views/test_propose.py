import json
from random import randint, sample
from string import ascii_letters
from typing import List

import pytest
from django.http import Http404
from django.urls import reverse
from factory import Faker

from donate_anything.item import views
from donate_anything.item.models import ProposedItem
from donate_anything.item.tests.factories import ItemFactory, WantedItemFactory
from donate_anything.users.tests.factories import UserFactory


pytestmark = pytest.mark.django_db


class TestViewEntityItemList:
    def test_list_active_entity_items(
        self, rf, charity, user, django_assert_max_num_queries
    ):
        # Create test data
        item_a = WantedItemFactory.create(
            item=ItemFactory.create(name="a"), charity=charity, condition=randint(0, 3)
        )
        item_k = WantedItemFactory.create(
            item=ItemFactory.create(name="k"), charity=charity, condition=randint(0, 3)
        )
        item_z = WantedItemFactory.create(
            item=ItemFactory.create(name="z"), charity=charity, condition=randint(0, 3)
        )
        request = rf.get("blah/")
        with django_assert_max_num_queries(3):
            response = views.list_active_entity_items(request, charity_id=charity.id)
        assert response.status_code == 200
        data = json.loads(response.content)["data"]
        assert data[0][0] == item_a.item.name
        assert data[0][1] == item_a.condition
        assert data[1][0] == item_k.item.name
        assert data[1][1] == item_k.condition
        assert data[2][0] == item_z.item.name
        assert data[2][1] == item_z.condition

    def test_list_active_entity_items_non_existent_entity(self, rf):
        with pytest.raises(Http404):
            request = rf.get("blah/")
            views.list_active_entity_items(request, 123)

    def test_list_org_items_view(self, client, charity):
        response = client.get(
            reverse("item:list-item-template", kwargs={"entity_id": charity.id})
        )
        assert response.status_code == 200
        assert response.context["id"] == charity.id
        assert response.context["name"] == charity.name

    def test_list_org_items_view_missing_entity(self, rf):
        with pytest.raises(Http404):
            request = rf.get("blah/")
            views.list_org_items_view(request, 123)


def _shortcut_test_proposed_template_test(
    proposed: ProposedItem, client, can_edit: bool = False, user=None
):
    client.force_login(proposed.user if user is None else user)
    response = client.get(
        reverse("item:list-proposed-template", kwargs={"proposed_item_pk": proposed.id})
    )
    assert response.status_code == 200
    assert response.context["proposed_item"] == proposed
    assert response.context["can_edit"] is can_edit


class TestViewEntityProposedItemList:
    def test_list_proposed_existing_item(self, rf, user, charity):
        items = sorted(ItemFactory.create_batch(10), key=lambda x: x.id)
        proposed = ProposedItem.objects.create(
            user=user, entity=charity, item=[x.id for x in items]
        )
        request = rf.get("blah")
        response = views.list_proposed_existing_item(request, proposed.id)
        assert response.status_code == 200
        data = json.loads(response.content)["data"]
        for d, item in zip(data, items):
            # Should be in the same order
            assert d == [item.id, item.name]

    def test_list_proposed_existing_item_not_exist(self, rf):
        request = rf.get("blah")
        with pytest.raises(Http404):
            views.list_proposed_existing_item(request, 123)

    def test_list_proposed_existing_names(self, rf, user, charity):
        names = [Faker("bs") for _ in range(10)]
        proposed = ProposedItem.objects.create(user=user, entity=charity, names=names)
        request = rf.get("blah")
        response = views.list_proposed_existing_item(request, proposed.id)
        assert response.status_code == 200
        data = json.loads(response.content)["data"]
        for d, name in zip(data, names):
            # Should be in the same order
            assert d == name

    def test_list_proposed_item_template(self, client, user, charity):
        proposed = ProposedItem.objects.create(entity=charity, user=user)
        _shortcut_test_proposed_template_test(proposed, client, can_edit=True)

    def test_list_proposed_item_template_cant_edit_not_owner(
        self, client, user, charity
    ):
        proposed = ProposedItem.objects.create(
            entity=charity, user=UserFactory.create()
        )
        _shortcut_test_proposed_template_test(proposed, client, user=user)

    def test_list_proposed_item_template_cant_edit_closed(self, client, user, charity):
        proposed = ProposedItem.objects.create(entity=charity, user=user, closed=True)
        _shortcut_test_proposed_template_test(proposed, client)

    def test_list_proposed_item_template_cant_edit_closed_and_not_owner(
        self, client, user, charity
    ):
        proposed = ProposedItem.objects.create(
            entity=charity, user=UserFactory.create(), closed=True
        )
        _shortcut_test_proposed_template_test(proposed, client, user=user)

    def test_list_proposed_item_template_missing_obj(self, rf):
        with pytest.raises(Http404):
            request = rf.get("blah")
            views.list_org_proposed_item_view(request, 123)


def _assert_response_form_create_update(response, user, charity, item, name):
    assert response.status_code == 200
    assert ProposedItem.objects.count() == 1
    obj = ProposedItem.objects.first()
    assert obj.user == user
    assert obj.entity == charity
    assert obj.item == item
    assert obj.names == name


def _format_list_to_str(elem: List) -> str:
    return ",".join(str(x) for x in elem)


def _random_string() -> str:
    return "".join(sample(ascii_letters, k=50))


class TestProposedItemForm:
    # Use client since it uses middleware
    # and it also allows for ignoring csrf stuff
    # Review csrf decorators: https://docs.djangoproject.com/en/3.0/ref/csrf/#django.views.decorators.csrf.csrf_protect
    view_url = reverse("item:proposed-item-form")

    def test_proposed_item_form_create(self, client, user, charity):
        item = [x.id for x in ItemFactory.create_batch(3)]
        name = [_random_string() for _ in range(3)]
        client.force_login(user)
        response = client.post(
            self.view_url,
            data={
                "entity": charity.id,
                "item": _format_list_to_str(item),
                "names": _format_list_to_str(name),
            },
        )
        _assert_response_form_create_update(response, user, charity, item, name)

    def test_proposed_item_form_update(self, client, user, charity):
        """The updating of the form"""
        item = [x.id for x in ItemFactory.create_batch(10)]
        name = [_random_string() for _ in range(10)]
        obj = ProposedItem.objects.create(
            user=user, entity=charity, item=item[:5], names=name[:5]
        )
        client.force_login(user)
        response = client.post(
            self.view_url,
            data={
                "id": obj.id,
                "item": _format_list_to_str(item),
                "names": _format_list_to_str(name),
            },
        )
        _assert_response_form_create_update(response, user, charity, item, name)

    def test_form_not_update_for_wrong_user(self, client, user, charity):
        item = [x.id for x in ItemFactory.create_batch(3)]
        name = [_random_string() for _ in range(3)]
        obj = ProposedItem.objects.create(
            user=user, entity=charity, item=item[:2], names=name[:2]
        )
        client.force_login(UserFactory.create())
        response = client.post(
            self.view_url,
            data={
                "id": obj.id,
                "item": _format_list_to_str(item),
                "names": _format_list_to_str(name),
            },
        )
        assert response.status_code == 200
        assert ProposedItem.objects.count() == 1
        obj = ProposedItem.objects.first()
        assert obj.item == item[:2]
        assert obj.names == name[:2]

    def test_proposed_item_form_id_and_entity_not_filled(self, client, user):
        client.force_login(user)
        response = client.post(self.view_url, data={"item": [1], "name": ["bs"]})
        assert response.status_code == 400
        errors = json.loads(response.content)["errors"]
        assert "entity" in errors

    def test_entity_does_not_exist(self, client, user):
        client.force_login(user)
        response = client.post(
            self.view_url, data={"entity": 123, "item": [1], "names": ["bs"]}
        )
        assert response.status_code == 400
        errors = json.loads(response.content)["errors"]
        assert "entity" in errors

    def test_proposed_item_form_empty_item(self, client, user, charity):
        client.force_login(user)
        response = client.post(self.view_url, data={"entity": charity.id, "item": [1]})
        assert response.status_code == 200

    def test_escape(self, client, user, charity):
        client.force_login(user)
        response = client.post(
            self.view_url, data={"entity": charity.id, "names": ["<p>hi</p>"]}
        )
        assert response.status_code == 200
        assert ProposedItem.objects.count() == 1
        obj = ProposedItem.objects.first()
        assert len(obj.names) == 1
        assert obj.names[0] == "&lt;p&gt;hi&lt;/p&gt;"

    def test_proposed_item_form_empty_name(self, client, user, charity):
        client.force_login(user)
        response = client.post(
            self.view_url, data={"entity": charity.id, "names": ["bs"]}
        )
        assert response.status_code == 200

    def test_not_appropriate_raise(self, client, user, charity):
        item = ItemFactory.create(is_appropriate=False)
        client.force_login(user)
        response = client.post(
            self.view_url, data={"entity": charity.id, "item": str(item.id)}
        )
        assert response.status_code == 400
        errors = json.loads(response.content)["errors"]
        assert "item" in errors
