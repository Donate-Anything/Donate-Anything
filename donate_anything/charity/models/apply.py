from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext_lazy as _


class Application(models.Model):
    id = models.BigAutoField(primary_key=True)
    submitted = models.DateField(auto_now_add=True, editable=False)

    # Default fields
    # In the voting process, there will be enough information in a single thread
    # that the names can be unique
    name = models.CharField(_("Name of Entity"), max_length=100)
    # Required. Certain exceptions like police department willing
    # to distribute stuffed animals at crime scenes. Social media is slight exception.
    # Can be just the domain. We can Google :)
    link = models.URLField(_("Link to website (or platform)"))
    description = models.TextField(_("Organization description"), max_length=1000)
    how_to_donate = models.TextField(_("How to Donate"), max_length=300)

    # Evidence Fields
    # Where are these things going? People in disaster zones? Country?
    specific_destination = models.CharField(_("Specific destination"), max_length=50)
    closed = models.BooleanField(default=False)
    # Cascade since it could've been a spam
    applier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Closed reason will be found in the thread.

    class Meta:
        abstract = True


class OrganizationApplication(Application):
    # Evidence Fields
    # Remember this is public. We don't expect private documentation
    # as there could be a database leak at some point.
    chapter_filing = models.TextField(_("Public Legal Documentation"), max_length=2000)
    # Extra for quicker evidence: social media posting,
    # link to your own donations page
    extra = JSONField(default=dict)

    def __str__(self):
        return self.name


class BusinessApplication(Application):
    # Min. 5 years. Special for some like recycling companies
    years_of_service = models.PositiveSmallIntegerField(_("Years of service"))
    # Extra reasons for doing this. It's ok to be honest :)
    reason = models.CharField(_("Reason for donations"), max_length=200)
    # Helps to identify who wants publicity, everyone does but,
    # trying to find the really bad businesses that don't deserve this platform.
    type_of_business = models.CharField(
        _("All your business model(s)."), max_length=120
    )


class Edits(models.Model):
    """Edits to something are specified in the edit itself.
    This allows the OP to merge the edit however he/she'd
    like. Also allows editor to mention a bunch of places
    for edits.
    """

    id = models.BigAutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    edit = models.TextField(max_length=5000)
    viewed = models.BooleanField(default=False)

    class Meta:
        abstract = True


class AppliedOrganizationEdit(Edits):
    proposed_entity = models.ForeignKey(
        OrganizationApplication, on_delete=models.SET_NULL, null=True
    )


class AppliedBusinessEdit(Edits):
    proposed_entity = models.ForeignKey(
        BusinessApplication, on_delete=models.SET_NULL, null=True
    )
