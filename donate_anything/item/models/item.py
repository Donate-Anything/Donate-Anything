from django.db import models

from donate_anything.charity.models import Charity


class Item(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    image = models.ImageField(blank=True, null=True)
    is_appropriate = models.BooleanField(default=True)


class WantedItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    # TODO Use a BRIN Index for Item
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    # TODO Add geolocation for charity for filtering
    #  for certain orgs like soup kitchens
    # Don't do it in this model... I think... This'll take experimenting
    # and deciding how the geo filtering would actually work.
