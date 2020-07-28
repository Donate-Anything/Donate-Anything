from factory import DjangoModelFactory, Faker, SubFactory

from donate_anything.charity.models import (
    AppliedBusinessEdit,
    AppliedOrganizationEdit,
    BusinessApplication,
    Charity,
    OrganizationApplication,
)
from donate_anything.users.tests.factories import UserFactory


# Core Model


class CharityFactory(DjangoModelFactory):
    name = Faker("company")
    link = Faker("url")
    description = Faker("text", max_nb_chars=1000)
    how_to_donate = Faker("text", max_nb_chars=300)

    class Meta:
        model = Charity


# Applied Models


class BusinessApplicationFactory(DjangoModelFactory):
    name = Faker("company")
    link = Faker("url")
    description = Faker("text", max_nb_chars=1000)
    how_to_donate = Faker("text", max_nb_chars=300)
    specific_destination = Faker("country")
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
    specific_destination = Faker("country")
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
