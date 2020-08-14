import logging
from email.utils import parseaddr

from anymail.exceptions import AnymailCancelSend
from anymail.signals import pre_send
from django.dispatch import receiver
from django_ses.signals import bounce_received, complaint_received

from donate_anything.users.models.user import BlacklistedEmail


logger = logging.getLogger(__name__)


# AWS SES handling: Object Types
# https://docs.aws.amazon.com/ses/latest/DeveloperGuide/notification-contents.html
@receiver(bounce_received)
def bounce_handler(sender, bounce_obj: dict, **kwargs):
    if bounce_obj.get("bounceType") == "Permanent" and bounce_obj.get(
        "bounceSubType", ""
    ) not in ("Suppressed", "OnAccountSuppressionList"):
        emails = {x["emailAddress"] for x in bounce_obj.get("bouncedRecipients", [])}
        blacklisted = tuple(
            x.email for x in BlacklistedEmail.objects.filter(email__in=emails)
        )
        BlacklistedEmail.objects.bulk_create(
            [BlacklistedEmail(email=x) for x in emails.difference(blacklisted)],
        )


@receiver(complaint_received)
def complaint_handler(sender, complaint_obj: dict, **kwargs):
    emails = {x["emailAddress"] for x in complaint_obj.get("complainedRecipients", [])}
    blacklisted = tuple(
        x.email for x in BlacklistedEmail.objects.filter(email__in=emails)
    )
    BlacklistedEmail.objects.bulk_create(
        [BlacklistedEmail(email=x) for x in emails.difference(blacklisted)],
    )
    if complaint_obj.get("complaintFeedbackType", "") == "virus":
        # An email was sent that looked like a virus (according to AWS SES)
        feedback_id = complaint_obj.get("feedbackId")
        feedback_type = complaint_obj.get("complaintFeedbackType")
        logger.error(f"Virus in email: ID: {feedback_id} type: {feedback_type}")


def ok_to_send(addr) -> bool:
    """Determines if an email is ok to send to
    based on prev. bounce and complaints.

    :param addr: The email address in the form of "Name" <email>
    :return email ok to send or not.
    """
    _, email = parseaddr(addr)  # just want the <email> part
    if BlacklistedEmail.objects.filter(email=email).exists():
        return False  # in the blocklist, so *not* OK to send
    return True  # *not* in the blocklist, so OK to send


@receiver(pre_send)
def filter_blacklisted_recipients(sender, message, **kwargs):
    # https://anymail.readthedocs.io/en/stable/sending/signals/#pre-send-signal
    # No test. Straight from docs.
    if not ok_to_send(message.from_email):
        raise AnymailCancelSend("Blocked from_email")
    message.to = [addr for addr in message.to if ok_to_send(addr)]
    message.cc = [addr for addr in message.cc if ok_to_send(addr)]
