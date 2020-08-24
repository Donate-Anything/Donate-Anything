import json
from random import randint

import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.urls import reverse

from donate_anything.charity.tests.factories import VerifiedAccountFactory
from donate_anything.item import views
from donate_anything.item.models import WantedItem
from donate_anything.item.tests.factories import ItemFactory, WantedItemFactory


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
        assert data[0] == [item_a.item.name, item_a.condition]
        assert data[1] == [item_k.item.name, item_k.condition]
        assert data[2] == [item_z.item.name, item_z.condition]

    def test_list_active_entity_items_if_can_delete(self, rf):
        account = VerifiedAccountFactory.create(accepted=True)
        item_a = WantedItemFactory.create(
            item=ItemFactory.create(name="a"), charity=account.charity
        )
        item_k = WantedItemFactory.create(
            item=ItemFactory.create(name="k"), charity=account.charity
        )
        request = rf.get("blah/")
        request.user = account.user
        response = views.list_active_entity_items(
            request, charity_id=account.charity.id
        )
        assert response.status_code == 200
        data = json.loads(response.content)["data"]
        assert data[0] == [item_a.item.name, item_a.condition, item_a.id]
        assert data[1] == [item_k.item.name, item_k.condition, item_k.id]

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

    def test_only_show_appropriate(self, charity, rf):
        # Create test data
        item_a = WantedItemFactory.create(
            item=ItemFactory.create(name="a"), charity=charity, condition=randint(0, 3)
        )
        WantedItemFactory.create(
            item=ItemFactory.create(name="k", is_appropriate=False),
            charity=charity,
            condition=randint(0, 3),
        )
        assert WantedItem.objects.filter(charity=charity).count() == 2
        request = rf.get("blah/")
        response = views.list_active_entity_items(request, charity_id=charity.id)
        assert response.status_code == 200
        data = json.loads(response.content)["data"]
        assert len(data) == 1
        assert data[0] == [item_a.item.name, item_a.condition]

    def test_delete_on_get_only(self, rf):
        request = rf.get("blah")
        response = views.delete_items(request, 123)
        assert response.status_code == 405

    def test_only_verified_account_delete(self, rf):
        account = VerifiedAccountFactory.create(accepted=True)
        item_a = WantedItemFactory.create(
            item=ItemFactory.create(name="a"),
            charity=account.charity,
            condition=randint(0, 3),
        )
        request = rf.post("blah")
        request.user = account.user
        response = views.delete_items(request, item_a.id)
        assert response.status_code == 200
        assert WantedItem.objects.count() == 0

    def test_only_admin_delete(self, rf, charity, admin_user):
        item_a = WantedItemFactory.create(
            item=ItemFactory.create(name="a"), charity=charity, condition=randint(0, 3)
        )
        request = rf.post("blah")
        request.user = admin_user
        response = views.delete_items(request, item_a.id)
        assert response.status_code == 200
        assert WantedItem.objects.count() == 0

    def test_not_authenticated_forbidden(self, rf, charity):
        item_a = WantedItemFactory.create(
            item=ItemFactory.create(name="a"), charity=charity, condition=randint(0, 3)
        )
        request = rf.post("blah")
        request.user = AnonymousUser()
        response = views.delete_items(request, item_a.id)
        assert response.status_code == 403
        assert WantedItem.objects.count() == 1

    def test_regular_user_forbidden(self, rf, charity, user):
        item_a = WantedItemFactory.create(
            item=ItemFactory.create(name="a"), charity=charity, condition=randint(0, 3)
        )
        request = rf.post("blah")
        request.user = user
        response = views.delete_items(request, item_a.id)
        assert response.status_code == 403
        assert WantedItem.objects.count() == 1

    def test_raise_404_if_missing(self, rf, admin_user):
        assert WantedItem.objects.count() == 0
        request = rf.post("blah")
        request.user = admin_user
        with pytest.raises(Http404):
            views.delete_items(request, 1234567890)
        assert WantedItem.objects.count() == 0
