import pytest

from donate_anything.item.tests.factories import (
    Category,
    CategoryFactory,
    Item,
    ItemFactory,
    WantedItem,
    WantedItemFactory,
)


pytestmark = pytest.mark.django_db


@pytest.fixture
def category() -> Category:
    return CategoryFactory()


@pytest.fixture
def item() -> Item:
    return ItemFactory()


@pytest.fixture
def wanted_item() -> WantedItem:
    return WantedItemFactory()
