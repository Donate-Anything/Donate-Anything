import pytest

from donate_anything.forum.models import Message, Thread


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("is_organization", [True, False])
def test_create_thread_on_apply(
    organization_application_suggested_edit,
    business_application_suggested_edit,
    is_organization,
):
    # Using these pytest fixtures automatically launch the signals.
    if is_organization:
        thread = Thread.objects.filter(type=1)
    else:
        thread = Thread.objects.filter(type=2)
    assert len(thread) == 1
    assert Message.objects.filter(thread=thread[0]).count() == 1


def test_create_thread_on_suggest_active_entity(entity_proposed_edit):
    # Using this pytest fixture automatically launch the signals.
    assert Thread.objects.count() == 1
    assert Thread.objects.first().type == 3
    assert Message.objects.count() == 1
