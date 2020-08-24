import json
from random import randint, sample
from string import ascii_letters
from typing import List

import pytest
from django.http import Http404
from django.urls import reverse
from factory import Faker

from donate_anything.item import views
from donate_anything.item.models.item import WANTED_ITEM_CONDITIONS, ProposedItem
from donate_anything.item.tests.factories import ItemFactory, WantedItemFactory
from donate_anything.users.tests.factories import UserFactory


pytestmark = pytest.mark.django_db


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
        item_condition = [randint(0, 3) for _ in range(len(items))]
        proposed = ProposedItem.objects.create(
            user=user,
            entity=charity,
            item=[x.id for x in items],
            item_condition=item_condition,
        )
        request = rf.get("blah")
        response = views.list_proposed_existing_item(request, proposed.id)
        assert response.status_code == 200
        data = json.loads(response.content)
        for d, item in zip(data["data"], items):
            # Should be in the same order
            assert d == [item.id, item.name]
        for condition, item_condition in zip(data["condition"], item_condition):
            assert item_condition == condition

    def test_list_proposed_existing_item_not_exist(self, rf):
        request = rf.get("blah")
        with pytest.raises(Http404):
            views.list_proposed_existing_item(request, 123)

    def test_list_proposed_nonexisting_names(self, rf, user, charity):
        names = [Faker("bs") for _ in range(10)]
        proposed = ProposedItem.objects.create(
            user=user,
            entity=charity,
            names=names,
            names_condition=[randint(0, 3) for _ in range(len(names))],
        )
        request = rf.get("blah")
        response = views.list_proposed_existing_item(request, proposed.id)
        assert response.status_code == 200
        data = json.loads(response.content)
        for d, name in zip(data["data"], names):
            # Should be in the same order
            assert d == name
        for condition, name in zip(data["condition"], names):
            assert name.names_condition == condition

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


def _assert_response_form_create_update(
    response, user, charity, item, item_condition, name, names_condition
):
    assert response.status_code == 200
    assert ProposedItem.objects.count() == 1
    obj: ProposedItem = ProposedItem.objects.first()
    assert obj.user == user
    assert obj.entity == charity
    assert obj.item == item
    assert obj.item_condition == item_condition
    assert obj.names == name
    assert obj.names_condition == names_condition


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
        item_condition = [randint(0, 3) for _ in range(len(item))]
        name = [_random_string() for _ in range(3)]
        names_condition = [randint(0, 3) for _ in range(len(name))]
        client.force_login(user)
        response = client.post(
            self.view_url,
            data={
                "entity": charity.id,
                "item": _format_list_to_str(item),
                "item_condition": _format_list_to_str(item_condition),
                "names": _format_list_to_str(name),
                "names_condition": _format_list_to_str(names_condition),
            },
        )
        _assert_response_form_create_update(
            response, user, charity, item, item_condition, name, names_condition
        )

    @pytest.mark.parametrize("attribute_name", ["names", "item"])
    @pytest.mark.parametrize("neg", [-2, 1])
    def test_attribute_and_condition_not_equal_in_length(
        self, attribute_name, client, user, charity, neg
    ):
        # Doesn't matter since we're stringifying everything
        array = [x.id for x in ItemFactory.create_batch(3)]
        array_condition = _format_list_to_str(
            [randint(0, 3) for _ in range((len(array) - neg))]
        )
        client.force_login(user)
        response = client.post(
            self.view_url,
            data={
                "entity": charity.id,
                attribute_name: _format_list_to_str(array),
                attribute_name + "_condition": array_condition,
            },
        )
        assert response.status_code == 400
        errors = json.loads(response.content)["errors"]
        assert attribute_name in errors
        assert attribute_name + "_condition" in errors

    def test_proposed_item_form_update(self, client, user, charity):
        """The updating of the form"""
        item = [x.id for x in ItemFactory.create_batch(10)]
        item_condition = [3] * len(item)
        name = [_random_string() for _ in range(10)]
        names_condition = [3] * len(name)
        obj = ProposedItem.objects.create(
            user=user, entity=charity, item=item[:5], names=name[:5]
        )
        client.force_login(user)
        response = client.post(
            self.view_url,
            data={
                "id": obj.id,
                "item": _format_list_to_str(item),
                "item_condition": _format_list_to_str(item_condition),
                "names": _format_list_to_str(name),
                "names_condition": _format_list_to_str(names_condition),
            },
        )
        _assert_response_form_create_update(
            response, user, charity, item, item_condition, name, names_condition
        )

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
                "item_condition": _format_list_to_str([3] * len(item)),
                "names": _format_list_to_str(name),
                "names_condition": _format_list_to_str([3] * len(name)),
            },
        )
        assert response.status_code == 200
        assert ProposedItem.objects.count() == 1
        obj = ProposedItem.objects.first()
        assert obj.item == item[:2]
        assert obj.names == name[:2]

    def test_proposed_item_form_id_and_entity_not_filled(self, client, user):
        client.force_login(user)
        response = client.post(
            self.view_url,
            data={
                "item": [1],
                "item_condition": [1],
                "name": ["bs"],
                "names_condition": [1],
            },
        )
        assert response.status_code == 400
        errors = json.loads(response.content)["errors"]
        assert "entity" in errors

    def test_entity_does_not_exist(self, client, user):
        client.force_login(user)
        response = client.post(
            self.view_url,
            data={
                "entity": 123,
                "item": [1],
                "item_condition": [1],
                "names": ["bs"],
                "names_condition": [1],
            },
        )
        assert response.status_code == 400
        errors = json.loads(response.content)["errors"]
        assert "entity" in errors

    def test_proposed_item_form_empty_item(self, client, user, charity):
        client.force_login(user)
        response = client.post(
            self.view_url,
            data={"entity": charity.id, "item": [1], "item_condition": [2]},
        )
        assert response.status_code == 200

    def test_escape(self, client, user, charity):
        client.force_login(user)
        response = client.post(
            self.view_url,
            data={"entity": charity.id, "names": ["<p>hi</p>"], "names_condition": [1]},
        )
        assert response.status_code == 200
        assert ProposedItem.objects.count() == 1
        obj = ProposedItem.objects.first()
        assert len(obj.names) == 1
        assert obj.names[0] == "&lt;p&gt;hi&lt;/p&gt;"

    def test_proposed_item_form_empty_name(self, client, user, charity):
        client.force_login(user)
        response = client.post(
            self.view_url,
            data={"entity": charity.id, "names": ["bs"], "names_condition": [1]},
        )
        assert response.status_code == 200

    def test_item_not_appropriate_raise(self, client, user, charity):
        item = ItemFactory.create(is_appropriate=False)
        client.force_login(user)
        response = client.post(
            self.view_url,
            data={"entity": charity.id, "item": str(item.id), "item_condition": [1]},
        )
        assert response.status_code == 400
        errors = json.loads(response.content)["errors"]
        assert "item" in errors

    def test_item_missing_condition(self, client, user, charity):
        item = ItemFactory.create(is_appropriate=False)
        client.force_login(user)
        response = client.post(
            self.view_url, data={"entity": charity.id, "item": str(item.id)},
        )
        assert response.status_code == 400
        errors = json.loads(response.content)["errors"]
        assert "item" in errors

    def test_name_missing_condition(self, client, user, charity):
        client.force_login(user)
        response = client.post(
            self.view_url, data={"entity": charity.id, "names": "bs"},
        )
        assert response.status_code == 400
        errors = json.loads(response.content)["errors"]
        assert "names" in errors

    @pytest.mark.parametrize("neg", [-2, 1])
    def test_item_condition_incorrect_length(self, client, user, charity, neg):
        item = ItemFactory.create(is_appropriate=False)
        client.force_login(user)
        response = client.post(
            self.view_url,
            data={
                "entity": charity.id,
                "item": str(item.id),
                "item_condition": [1] * (1 - neg),
            },
        )
        assert response.status_code == 400
        errors = json.loads(response.content)["errors"]
        assert "item" in errors

    @pytest.mark.parametrize("neg", [-2, 1])
    def test_name_condition_incorrect_length(self, client, user, charity, neg):
        client.force_login(user)
        response = client.post(
            self.view_url,
            data={
                "entity": charity.id,
                "names": "bs",
                "item_condition": [2] * (1 - neg),
            },
        )
        assert response.status_code == 400
        errors = json.loads(response.content)["errors"]
        assert "names" in errors

    @pytest.mark.parametrize("incorrect", [-1, len(WANTED_ITEM_CONDITIONS)])
    def test_item_condition_invalid_choice(self, client, user, charity, incorrect):
        item = ItemFactory.create(is_appropriate=False)
        client.force_login(user)
        response = client.post(
            self.view_url,
            data={
                "entity": charity.id,
                "item": str(item.id),
                "item_condition": [incorrect],
            },
        )
        assert response.status_code == 400
        errors = json.loads(response.content)["errors"]
        assert "item" in errors

    @pytest.mark.parametrize("incorrect", [-1, len(WANTED_ITEM_CONDITIONS)])
    def test_name_condition_invalid_choice(self, client, user, charity, incorrect):
        client.force_login(user)
        response = client.post(
            self.view_url,
            data={"entity": charity.id, "names": "bs", "names_condition": [incorrect]},
        )
        assert response.status_code == 400
        errors = json.loads(response.content)["errors"]
        assert "names_condition" in errors
