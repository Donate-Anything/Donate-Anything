import pytest

from donate_anything.charity.tests.factories import Charity, CharityFactory
from donate_anything.users.models import User
from donate_anything.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def charity() -> Charity:
    return CharityFactory()
