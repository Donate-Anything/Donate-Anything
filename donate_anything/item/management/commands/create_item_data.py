from django.conf import settings
from django.core.management.base import BaseCommand

from donate_anything.charity.models import Charity
from donate_anything.item.models import Item, WantedItem
from donate_anything.item.tests.factories import WantedItemFactory


class Command(BaseCommand):
    help = (
        "Generates test data items. Used in conjunction with"
        "core test data for generation."
    )
    requires_migrations_checks = True

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise Exception("You cannot use this command in production.")
        print("Creating Item app data.")
        org_1 = Charity.objects.create(
            name="Org 1",
            link="https://google.com/",
            description="Desc.",
            how_to_donate="Address",
        )
        org_2 = Charity.objects.create(
            name="Org 2",
            link="https://google.com/",
            description="Desc.",
            how_to_donate="Address",
        )
        org_3 = Charity.objects.create(
            name="Org 3",
            link="https://google.com/",
            description="Desc.",
            how_to_donate="Address",
        )

        item_1 = Item.objects.create(name="pan")
        item_2 = Item.objects.create(name="canned food")
        Item.objects.create(name="chair")
        item_3 = Item.objects.create(name="fork")
        item_4 = Item.objects.create(name="blood")

        WantedItem.objects.create(item=item_1, charity=org_1)  # 3 orgs
        WantedItem.objects.create(item=item_2, charity=org_1)  # 2 orgs
        WantedItem.objects.create(item=item_3, charity=org_1)  # 2 orgs
        WantedItem.objects.create(item=item_4, charity=org_1)  # 1 org

        WantedItem.objects.create(item=item_1, charity=org_2)
        WantedItem.objects.create(item=item_2, charity=org_2)
        WantedItem.objects.create(item=item_1, charity=org_3)
        WantedItem.objects.create(item=item_3, charity=org_3)

        # For testing pagination - change to 1 in paginating
        WantedItemFactory.create_batch(25, item=item_1)
        print("Finished creating Item app data.")
