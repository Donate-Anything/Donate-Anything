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
