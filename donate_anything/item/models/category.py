from django.db import models

from donate_anything.charity.models import Charity


CATEGORY_TYPES = (
    (0, "Financial"),
    (1, "Clothing"),  # usually in decent condition. Poor condition become rags :P
    (2, "Kitchenware"),  # pots n pans
    (3, "Books and Media"),  # magazines, newspapers
    (4, "Toys and Games"),  # board games, toys :P
    (5, "Art"),  # paint brushes, canvases, sketch pencils
    (6, "Hygiene"),  # toothbrushes
    (7, "Sports"),  # footballs
    (8, "Furniture"),  # chairs, mattresses
    (9, "Electronics"),  # Rasp Pi's, HDMI cords, a tv?
    (10, "Internal Health"),  # e.g. blood, organs
    (11, "School Supplies"),  # pencils, paper. Typically needs to be good condition
    (12, "Linen"),  # bed sheets, sleeping bags?
    # KNOW THE DIFFERENCE
    (13, "Recyclables"),  # some people just want to figure out what they can recycle
    (14, "Compost"),  # some people just want to figure out what they can compost
    (15, "Food and Liquids"),  # food kitchens, homeless shelters
    (16, "Miscellaneous"),  # Typically recyclables
)


class Category(models.Model):
    """An item CAN be in a category, but really it's
    just what category this charity supports, not necessarily
    the items themselves.
    """

    id = models.BigAutoField(primary_key=True)
    charity = models.ForeignKey(Charity, on_delete=models.CASCADE)
    category = models.PositiveSmallIntegerField(choices=CATEGORY_TYPES)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["charity", "category"], name="charity_supports_category"
            )
        ]
