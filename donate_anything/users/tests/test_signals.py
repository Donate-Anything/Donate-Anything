import pytest
from django_ses.signals import bounce_received, complaint_received

from donate_anything.users.models import BlacklistedEmail
from donate_anything.users.signals import ok_to_send


pytestmark = pytest.mark.django_db


_test_email_1 = "test1@test.com"


_bounce_obj = {
    "bounceType": "Permanent",
    "bounceSubType": "General",
    "bouncedRecipients": [
        {"emailAddress": _test_email_1},
        {"emailAddress": "test2@test.com"},
    ],
}


_complaint_obj = {
    "complainedRecipients": [
        {"emailAddress": _test_email_1},
        {"emailAddress": "test2@test.com"},
        {"emailAddress": "test3@test.com"},
    ]
}


class TestBlacklistEmail:
    def test_ok_to_send(self):
        email = "fred@example.com"
        assert ok_to_send(addr=f'"Fred" <{email}>')
        BlacklistedEmail.objects.create(email=email)
        assert not ok_to_send(f'"Fred" <{email}>')

    def test_hard_permanent_bounce(self):
        bounce_received.send(None, bounce_obj=_bounce_obj)
        assert BlacklistedEmail.objects.count() == 2

    @pytest.mark.parametrize("bounce_type", ["Transient", "Undefined"])
    # Only some transient and undefined. since we're only testing combos
    @pytest.mark.parametrize(
        "sub_bounce_type",
        ["Undetermined", "Suppressed", "OnAccountSuppressionList", "MailboxFull"],
    )
    def test_invalid_bounce(self, bounce_type, sub_bounce_type):
        obj = {
            "bounceType": bounce_type,
            "bounceSubType": sub_bounce_type,
            "bouncedRecipients": [{"emailAddress": _test_email_1}],
        }
        bounce_received.send(None, bounce_obj=obj)
        assert BlacklistedEmail.objects.count() == 0

    def test_ignore_duplicate_blacklist_bounce(self):
        BlacklistedEmail.objects.create(email=_test_email_1)
        assert BlacklistedEmail.objects.count() == 1
        # Should not raise an error
        bounce_received.send(None, bounce_obj=_bounce_obj)
        assert BlacklistedEmail.objects.count() == 2
        # Assure get returns one object
        BlacklistedEmail.objects.get(email=_test_email_1)

    def test_complaint_received(self):
        complaint_received.send(None, complaint_obj=_complaint_obj)
        assert BlacklistedEmail.objects.count() == 3

    def test_ignore_duplicate_blacklist_complain(self):
        BlacklistedEmail.objects.create(email=_test_email_1)
        assert BlacklistedEmail.objects.count() == 1
        complaint_received.send(None, complaint_obj=_complaint_obj)
        assert BlacklistedEmail.objects.count() == 3
        BlacklistedEmail.objects.get(email=_test_email_1)
