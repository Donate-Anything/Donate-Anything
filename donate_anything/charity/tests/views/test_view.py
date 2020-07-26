import json
from datetime import datetime

import pytest
from django.http import Http404
from django.urls import reverse

from donate_anything.charity.models import AppliedBusinessEdit, AppliedOrganizationEdit
from donate_anything.charity.tests.factories import (
    AppliedBusinessEditFactory,
    AppliedOrganizationEditFactory,
)
from donate_anything.charity.views.list import organization


pytestmark = pytest.mark.django_db


def _format_datetime_to_content_str(dt: datetime):
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


class TestOrganizationView:
    def test_organization_view_success(self, charity, client):
        response = client.get(
            reverse("charity:organization", kwargs={"pk": charity.id})
        )
        assert response.status_code == 200
        assert response.context["name"] == charity.name
        assert response.context["description"] == charity.description
        assert response.context["how_to_donate"] == charity.how_to_donate

    def test_organization_view_not_found(self, rf):
        fake_id = 1
        request = rf.get(reverse("charity:organization", kwargs={"pk": fake_id}))
        with pytest.raises(Http404):
            organization(request, fake_id)


class TestViewEdits:
    @pytest.mark.parametrize(
        "factory,model,view",
        [
            (
                AppliedOrganizationEditFactory,
                AppliedOrganizationEdit,
                "charity:applied-organization-edits",
            ),
            (
                AppliedBusinessEditFactory,
                AppliedBusinessEdit,
                "charity:applied-business-edits",
            ),
        ],
    )
    def test_applied_organization_edits(
        self,
        organization_application,
        business_application,
        client,
        user,
        factory,
        model,
        view,
    ):
        client.force_login(user)
        if factory == AppliedOrganizationEditFactory:
            factory.create_batch(30, proposed_entity=organization_application)
            response = client.get(
                reverse(view, kwargs={"pk": organization_application.id})
                + "?page=2&unseen=1"
            )
        else:
            factory.create_batch(30, proposed_entity=business_application)
            response = client.get(
                reverse(view, kwargs={"pk": business_application.id})
                + "?page=2&unseen=1"
            )
        assert response.status_code == 200
        content = json.loads(response.content.decode())["data"]
        assert len(content) == 5, "Pagination is 25 in length. 30-25 is 5."
        assert len(content[0]) == 5, "pk, username, edit, created, updated"
        obj = model.objects.get(id=int(content[0][0]))
        assert content[0][1] == obj.user.username
        assert content[0][2] == obj.edit
        assert content[0][3] == _format_datetime_to_content_str(obj.created)
        assert content[0][4] == _format_datetime_to_content_str(obj.updated)

    @pytest.mark.parametrize(
        "factory,view",
        [
            (AppliedOrganizationEditFactory, "charity:applied-organization-edits"),
            (AppliedBusinessEditFactory, "charity:applied-business-edits"),
        ],
    )
    def test_show_only_unseen(
        self,
        organization_application,
        business_application,
        client,
        user,
        factory,
        view,
    ):
        client.force_login(user)
        if factory == AppliedOrganizationEditFactory:
            not_seen = factory.create(
                proposed_entity=organization_application, viewed=False
            )
            factory.create(proposed_entity=organization_application, viewed=True)
            response = client.get(
                reverse(view, kwargs={"pk": organization_application.id}) + "?unseen=1"
            )
        else:
            not_seen = factory.create(
                proposed_entity=business_application, viewed=False
            )
            factory.create(proposed_entity=business_application, viewed=True)
            response = client.get(
                reverse(view, kwargs={"pk": business_application.id}) + "?unseen=1"
            )
        assert response.status_code == 200
        content = json.loads(response.content.decode())["data"]
        assert len(content) == 1, "Should only see the not-closed/read one."
        assert content[0] == [
            not_seen.id,
            not_seen.user.username,
            not_seen.edit,
            _format_datetime_to_content_str(not_seen.created),
            _format_datetime_to_content_str(not_seen.updated),
        ]

    @pytest.mark.parametrize(
        "factory,view",
        [
            (AppliedOrganizationEditFactory, "charity:applied-organization-edits"),
            (AppliedBusinessEditFactory, "charity:applied-business-edits"),
        ],
    )
    def test_show_all_edits(
        self,
        organization_application,
        business_application,
        client,
        user,
        factory,
        view,
    ):
        self.test_show_only_unseen(
            organization_application, business_application, client, user, factory, view
        )
        if factory == AppliedOrganizationEditFactory:
            response = client.get(
                reverse(view, kwargs={"pk": organization_application.id})
            )
        else:
            response = client.get(reverse(view, kwargs={"pk": business_application.id}))
        assert response.status_code == 200
        content = json.loads(response.content.decode())["data"]
        assert len(content) == 2
        seen = []
        for x in content:
            assert len(x) == 6
            seen.append(x[5])
        assert set(seen) == {True, False}
