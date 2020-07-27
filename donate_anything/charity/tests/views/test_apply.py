import json

import pytest
from django.urls import reverse

from donate_anything.charity.models import AppliedBusinessEdit, AppliedOrganizationEdit


pytestmark = pytest.mark.django_db
_edit_text = "a"


def _success_suggest_edit(entity_id, client, view, user, create=True):
    client.force_login(user)
    data = {"id": entity_id, "edit": _edit_text, "create": create}
    response = client.post(reverse(view), data=data)
    assert response.status_code == 200, response.content
    return response


class TestSuggestEdit:
    views = ["charity:edit-suggest-applied-org", "charity:edit-suggest-applied-bus"]

    # form: id, edit, create
    @pytest.mark.parametrize("view", views)
    def test_suggest_new_edit(
        self, organization_application, business_application, client, user, view
    ):
        if view == "charity:edit-suggest-applied-org":
            response = _success_suggest_edit(
                organization_application.id, client, view, user
            )
            data = json.loads(response.content)
            assert AppliedOrganizationEdit.objects.get(id=data["id"]).edit == _edit_text
        else:
            response = _success_suggest_edit(
                business_application.id, client, view, user
            )
            data = json.loads(response.content)
            assert AppliedBusinessEdit.objects.get(id=data["id"]).edit == _edit_text
        assert data["username"] == user.get_username()

    @pytest.mark.parametrize("view", views)
    def test_cannot_find_entity_id(self, view, client, user):
        client.force_login(user)
        data = {"id": 0, "edit": _edit_text, "create": True}
        response = client.post(reverse(view), data=data)
        assert response.status_code == 400

    @pytest.mark.parametrize("view", views)
    def test_update_suggested_edit(
        self,
        organization_application_suggested_edit,
        business_application_suggested_edit,
        client,
        user,
        view,
    ):
        organization_application_suggested_edit.user = user
        organization_application_suggested_edit.save(update_fields=["user"])
        business_application_suggested_edit.user = user
        business_application_suggested_edit.save(update_fields=["user"])
        if view == "charity:edit-suggest-applied-org":
            _success_suggest_edit(
                organization_application_suggested_edit.id,
                client,
                view,
                user,
                create=False,
            )
        else:
            _success_suggest_edit(
                business_application_suggested_edit.id, client, view, user, create=False
            )

    @pytest.mark.parametrize("view", views)
    def test_cannot_edit_others_suggested_edits(
        self,
        organization_application_suggested_edit,
        business_application_suggested_edit,
        client,
        user,
        view,
    ):
        client.force_login(user)
        if view == "charity:edit-suggest-applied-org":
            data = {
                "id": organization_application_suggested_edit.id,
                "edit": _edit_text,
                "create": False,
            }
        else:
            data = {
                "id": business_application_suggested_edit.id,
                "edit": _edit_text,
                "create": False,
            }
        response = client.post(reverse(view), data=data)
        assert response.status_code == 403

    @pytest.mark.parametrize("view", views)
    def test_cannot_find_edit_id(self, view, client, user):
        client.force_login(user)
        data = {"id": 0, "edit": _edit_text, "create": False}
        response = client.post(reverse(view), data=data)
        assert response.status_code == 403, response.content
