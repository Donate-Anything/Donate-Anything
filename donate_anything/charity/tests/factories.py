from factory import DjangoModelFactory, Faker, SubFactory

from donate_anything.charity.models import (
    AppliedBusinessEdit,
    AppliedOrganizationEdit,
    BusinessApplication,
    Charity,
    OrganizationApplication,
    ProposedEdit,
)
from donate_anything.users.models.charity import VerifiedAccount
from donate_anything.users.tests.factories import UserFactory


# Core Model


class CharityFactory(DjangoModelFactory):
    name = Faker("company")
    link = Faker("url")
    description = Faker("text", max_nb_chars=1000)
    how_to_donate = Faker("text", max_nb_chars=300)

    class Meta:
        model = Charity


class VerifiedAccountFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    charity = SubFactory(CharityFactory)
    reason = Faker("sentence")

    class Meta:
        model = VerifiedAccount
        django_get_or_create = ["user"]


# Applied Models


class BusinessApplicationFactory(DjangoModelFactory):
    name = Faker("company")
    link = Faker("url")
    description = Faker("text", max_nb_chars=1000)
    how_to_donate = Faker("text", max_nb_chars=300)
    specific_destination = Faker("country_code")
    applier = SubFactory(UserFactory)
    years_of_service = Faker("pyint")
    reason = Faker("bs")
    type_of_business = Faker("job")

    class Meta:
        model = BusinessApplication


class OrganizationApplicationFactory(DjangoModelFactory):
    name = Faker("company")
    link = Faker("url")
    description = Faker("text", max_nb_chars=1000)
    how_to_donate = Faker("text", max_nb_chars=300)
    specific_destination = Faker("country_code")
    applier = SubFactory(UserFactory)
    chapter_filing = Faker("text", max_nb_chars=2000)

    class Meta:
        model = OrganizationApplication


class AppliedBusinessEditFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    edit = Faker("text", max_nb_chars=5000)
    proposed_entity = SubFactory(BusinessApplicationFactory)

    class Meta:
        model = AppliedBusinessEdit


class AppliedOrganizationEditFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    edit = Faker("text", max_nb_chars=5000)
    proposed_entity = SubFactory(OrganizationApplicationFactory)

    class Meta:
        model = AppliedOrganizationEdit


class ProposedEditFactory(DjangoModelFactory):
    entity = SubFactory(CharityFactory)
    user = SubFactory(UserFactory)

    class Meta:
        model = ProposedEdit
        django_get_or_create = ["entity", "user"]
