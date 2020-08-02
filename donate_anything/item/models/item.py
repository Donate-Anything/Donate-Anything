from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import BrinIndex, GinIndex
from django.db import models

from donate_anything.charity.models import Charity


_item_max_length = 100


class Item(models.Model):
    id = models.BigAutoField(primary_key=True)
    # TODO Some items need to be the same, e.g. pants + jeans or tshirt + t-shirt
    #  This requires a self FK and a little rewriting of views
    name = models.CharField(max_length=_item_max_length, unique=True, db_index=True)
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

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super(Item, self).save(*args, **kwargs)


class WantedItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    # TODO Add condition of item: good, ok, bad
    item = models.ForeignKey(Item, on_delete=models.CASCADE, db_index=False)
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    # TODO Add geolocation for charity for filtering
    #  for certain orgs like soup kitchens
    # Don't do it in this model... I think... This'll take experimenting
    # and deciding how the geo filtering would actually work.
    # Plus... IP Addr. + GeoMax makes Lambda not happy and Privacy no good.

    class Meta:
        indexes = (BrinIndex(fields=["item"]),)
        constraints = [
            models.UniqueConstraint(
                fields=["charity", "item"], name="charity_need_item"
            )
        ]

    def __str__(self):
        return f"{self.charity} wants {self.item}"


class ProposedItem(models.Model):
    """User inputted items that can be merged.
    """

    id = models.BigAutoField(primary_key=True)
    entity = models.ForeignKey(Charity, on_delete=models.SET_NULL, null=True)
    # Delete user in case of spam
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Actual items
    item = ArrayField(models.BigIntegerField(), size=10000, default=list)
    names = ArrayField(
        models.CharField(max_length=_item_max_length), size=1000, default=list
    )
    closed = models.BooleanField(default=False)
