import pytest

from donate_anything.charity.forms import ExistingSuggestEditForm, OrganizationForm
from donate_anything.charity.models import OrganizationApplication, ProposedEdit
from donate_anything.charity.tests.factories import (
    CharityFactory,
    OrganizationApplicationFactory,
)


pytestmark = pytest.mark.django_db


class TestOrganizationForm:
    def test_extra_social_media_added(self, user):
        proto_application = OrganizationApplicationFactory.build()
        social_media = "https://google.com/"
        form = OrganizationForm(
            {
                "name": proto_application.name,
                "link": proto_application.link,
                "description": proto_application.description,
                "how_to_donate": proto_application.how_to_donate,
                "specific_destination": proto_application.specific_destination,
                "chapter_filing": proto_application.chapter_filing,
                "social_media": social_media,
            }
        )
        form.applier = user
        assert form.is_valid()

        form.save()
        assert OrganizationApplication.objects.count() == 1
        obj = OrganizationApplication.objects.first()
        assert obj.extra == {"social_media": social_media}

    def test_empty_extra(self, user):
        proto_application = OrganizationApplicationFactory.build()
        form = OrganizationForm(
            {
                "name": proto_application.name,
                "link": proto_application.link,
                "description": proto_application.description,
                "how_to_donate": proto_application.how_to_donate,
                "specific_destination": proto_application.specific_destination,
                "chapter_filing": proto_application.chapter_filing,
            }
        )
        form.applier = user
        assert form.is_valid()

        form.save()
        assert OrganizationApplication.objects.count() == 1
        obj = OrganizationApplication.objects.first()
        assert obj.extra == {}


class TestExistingSuggestEditForm:
    """Assumes entity already exists"""

    @pytest.mark.parametrize("is_verified", [True, False])
    def test_no_fields_changed(self, charity, user, is_verified):
        form = ExistingSuggestEditForm(
            {
                "link": charity.link,
                "description": charity.description,
                "how_to_donate": charity.how_to_donate,
                "commit_message": "Reason",
            },
            {"logo": charity.logo},
            is_verified=is_verified,
        )
        form.user = user
        form.entity = charity.id

        assert not form.is_valid()
        assert len(form.errors) == 1

    @pytest.mark.parametrize(
        "link,description,how_to,logo",
        [
            ("a", "", "", None),
            ("", "a", "", None),
            ("", "", "a", None),
            ("", "", "", True),
        ],
    )
    def test_at_least_one_field_filled(
        self, charity, user, link, description, how_to, logo
    ):
        if logo:
            logo = CharityFactory.create().logo
        form = ExistingSuggestEditForm(
            {
                "link": charity.link + link,
                "description": charity.description + description,
                "how_to_donate": charity.how_to_donate + how_to,
                "commit_message": "Reason",
            },
            {"logo": logo if logo else charity.logo},
            is_verified=True,
        )
        form.user = user
        form.entity = charity.id
        assert form.is_valid(), form.errors
        form.save()
        assert ProposedEdit.objects.count() == 1
