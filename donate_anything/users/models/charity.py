from django.conf import settings
from django.db import models


class VerifiedAccount(models.Model):
    """A VerifiedAccount has more control over what is merged
    into the organization's descriptions and items list.

    Adding these can only be done through the admin, and
    a user is manually created rather than having people
    create an account first. We'll create a temporary password.
    Users can edit their emails later.
    """

    # TODO Implement quick switch between user accounts in html.
    # We want to make sure user accounts are separate for each organization
    # in case of a security breach on either end
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, primary_key=True, on_delete=models.CASCADE
    )
    # Don't set charity to pk or OneToOne since in the future
    # we could allow multiple accounts.
    charity = models.ForeignKey("charity.Charity", on_delete=models.CASCADE)
    # Proof of validity for tracking records
    reason = models.TextField(max_length=300)

    # Accepted means account is currently verified
    accepted = models.BooleanField(default=False)
    submitted_on = models.DateField(auto_now_add=True, editable=False)
    verified_on = models.DateField(null=True, blank=True)
