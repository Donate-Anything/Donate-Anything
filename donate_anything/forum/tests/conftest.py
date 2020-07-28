import pytest

from donate_anything.forum.models import Message, Thread, UserVote
from donate_anything.forum.tests.factories import (
    MessageFactory,
    ThreadFactory,
    UserVoteFactory,
)


pytestmark = pytest.mark.django_db


@pytest.fixture
def thread() -> Thread:
    return ThreadFactory()


@pytest.fixture
def message() -> Message:
    return MessageFactory()


@pytest.fixture
def user_vote() -> UserVote:
    return UserVoteFactory()
