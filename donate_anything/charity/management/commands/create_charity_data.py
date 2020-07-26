from random import randint, sample

from django.conf import settings
from django.core.management.base import BaseCommand

from donate_anything.charity.tests.factories import (
    AppliedBusinessEditFactory,
    AppliedOrganizationEditFactory,
    BusinessApplicationFactory,
    CharityFactory,
    OrganizationApplicationFactory,
    ProposedBusinessItem,
    ProposedOrganizationItem,
)
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
        print("Creating Charity app data.")

        # Create some charities
        CharityFactory.create_batch(5)
        # Create applications
        org_apps = OrganizationApplicationFactory.create_batch(5)
        bus_apps = BusinessApplicationFactory.create_batch(5)

        # Create some edits
        # Last one won't have any edits since it's the newest
        AppliedOrganizationEditFactory.create_batch(
            randint(3, 10), proposed_entity=org_apps[0]
        )
        for org in org_apps[1:-1]:
            AppliedOrganizationEditFactory.create_batch(30, proposed_entity=org)

        AppliedBusinessEditFactory.create_batch(30, proposed_entity=bus_apps[0])
        for bus in bus_apps[1:-1]:
            AppliedBusinessEditFactory.create_batch(randint(3, 10), proposed_entity=bus)

        # Create some items for them
        random_items = WantedItemFactory.create_batch(20)
        # Last and second to last won't have proposed items since they're "new"
        for org in org_apps[:-2]:
            ProposedOrganizationItem.objects.create(
                item=sample(
                    [x.item.id for x in random_items], k=randint(6, len(random_items))
                ),
                entity=org,
            )

        for bus in bus_apps[:-2]:
            ProposedBusinessItem.objects.create(
                item=sample(
                    [x.id for x in random_items], k=randint(6, len(random_items))
                ),
                entity=bus,
            )

        print("Finished creating Charity app data.")
