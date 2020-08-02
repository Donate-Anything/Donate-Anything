import pytest

from donate_anything.forum.models import Message, Thread
from donate_anything.item.models import ProposedItem
from donate_anything.item.tests.factories import ItemFactory


pytestmark = pytest.mark.django_db


def test_create_thread_proposed_item(charity, user):
    item = ItemFactory.create()
    ProposedItem.objects.create(entity=charity, user=user, item=[item.id])
    assert Thread.objects.count() == 1
    assert Message.objects.count() == 1
    thread = Thread.objects.first()
    assert thread.type == 4
    message = Message.objects.first()
    assert message.thread == thread
