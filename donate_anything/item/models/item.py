from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import BrinIndex, GinIndex
from django.db import models
from django.utils.functional import cached_property

from donate_anything.charity.models import Charity


_item_max_length = 100


class Item(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=_item_max_length, unique=True, db_index=True)
    image = models.ImageField(blank=True, null=True)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
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

    @cached_property
    def has_children(self) -> bool:
        return Item.objects.filter(parent_id=self.id).exists()

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super(Item, self).save(*args, **kwargs)


WANTED_ITEM_CONDITIONS = (
    (0, "Poor"),  # Completely ripped
    (1, "Used - Acceptable"),  # Decent but obvious markings
    (2, "Used - Very Good"),
    (3, "Brand New"),
)


class WantedItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    # Conditions work by seeing the number and up.
    # If you choose 0, then you'll get conditions from 0-3
    condition = models.PositiveSmallIntegerField(
        choices=WANTED_ITEM_CONDITIONS, default=3
    )
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
    item = ArrayField(models.BigIntegerField(), size=20000, default=list, blank=True)
    item_condition = ArrayField(
        models.PositiveSmallIntegerField(choices=WANTED_ITEM_CONDITIONS),
        size=20000,
        default=list,
        blank=True,
    )
    names = ArrayField(
        models.CharField(max_length=_item_max_length),
        size=1500,
        default=list,
        blank=True,
    )
    names_condition = ArrayField(
        models.PositiveSmallIntegerField(choices=WANTED_ITEM_CONDITIONS),
        size=1500,
        default=list,
        blank=True,
    )
    closed = models.BooleanField(default=False)
