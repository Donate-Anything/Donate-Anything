from factory import DjangoModelFactory, Faker

from donate_anything.charity.models import Charity


class CharityFactory(DjangoModelFactory):
    name = Faker("company")
    link = Faker("url")
    description = Faker("text")
    how_to_donate = Faker("text")

    class Meta:
        model = Charity
