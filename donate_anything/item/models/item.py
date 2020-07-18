from django.contrib.postgres.indexes import BrinIndex, GinIndex
from django.db import models

from donate_anything.charity.models import Charity


class Item(models.Model):
    id = models.BigAutoField(primary_key=True)
    # TODO Some items need to be the same, e.g. pants + jeans or tshirt + t-shirt
    # This requires a self FK and a little rewriting of views
    name = models.CharField(max_length=255, unique=True, db_index=False)
    image = models.ImageField(blank=True, null=True)
    is_appropriate = models.BooleanField(default=True)

    class Meta:
        indexes = (
            GinIndex(
                name="item_name_sim_gin_index",
                fields=("name",),
                opclasses=("gin_trgm_ops",),
            ),
        )


class WantedItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, db_index=False)
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    # TODO Add geolocation for charity for filtering
    #  for certain orgs like soup kitchens
    # Don't do it in this model... I think... This'll take experimenting
    # and deciding how the geo filtering would actually work.
    # Plus... IP Addr. + GeoMax makes Lambda not happy and Privacy no good.

    class Meta:
        indexes = (BrinIndex(fields=["item"]),)
