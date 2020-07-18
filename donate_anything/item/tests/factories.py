from random import choice

from factory import DjangoModelFactory, Faker, SubFactory

from donate_anything.charity.tests.factories import CharityFactory
from donate_anything.item.models import Category, Item, WantedItem
from donate_anything.item.models.category import CATEGORY_TYPES


class CategoryFactory(DjangoModelFactory):
    charity = SubFactory(CharityFactory)
    category = choice(CATEGORY_TYPES)[0]

    class Meta:
        model = Category
        django_get_or_create = ["charity"]


class ItemFactory(DjangoModelFactory):
    name = Faker("bs")
    image = Faker("image_url")

    class Meta:
        model = Item


class WantedItemFactory(DjangoModelFactory):
    charity = SubFactory(CharityFactory)
    item = SubFactory(ItemFactory)

    class Meta:
        model = WantedItem
        django_get_or_create = ["charity", "item"]
