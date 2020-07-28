from django.conf import settings
from django.db import models


class Charity(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)

    # All charities that are 501c3: https://www.irs.gov/charities-non-profits/tax-exempt-organization-search
    # Any charity that is not first
    # verified must provide a link.
    link = models.URLField()

    # However, description must follow
    # specific format if the user adding
    # charity is not verified via domain email.
    description = models.TextField(max_length=1000)
    # Address or drop off instructions
    how_to_donate = models.TextField(max_length=300)

    # Items are in a M2M ES model

    def __str__(self):
        return self.name


class ProposedEdit(models.Model):
    id = models.BigAutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    commit_message = models.TextField(max_length=300)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    entity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    link = models.URLField(blank=True, null=True)
    description = models.TextField(max_length=1000, blank=True, null=True)
    how_to_donate = models.TextField(max_length=300, blank=True, null=True)
