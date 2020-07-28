from factory import DjangoModelFactory, Faker, SubFactory

from donate_anything.forum.models import Message, Thread, UserVote
from donate_anything.users.tests.factories import UserFactory


class ThreadFactory(DjangoModelFactory):
    title = Faker("bs")
    type = Faker("random_int", min=0, max=1)

    class Meta:
        model = Thread


class MessageFactory(DjangoModelFactory):
    thread = SubFactory(ThreadFactory)
    user = SubFactory(UserFactory)
    message = Faker("paragraph")

    class Meta:
        model = Message
        django_get_or_create = ["thread", "user"]


class UserVoteFactory(DjangoModelFactory):
    thread = SubFactory(ThreadFactory)
    direction = Faker("pybool")
    user = SubFactory(UserFactory)

    class Meta:
        model = UserVote
        django_get_or_create = ["thread", "user"]
