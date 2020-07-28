from random import randint

from django.conf import settings
from django.core.management.base import BaseCommand

from donate_anything.forum.models import Thread
from donate_anything.forum.models.forum import THREAD_TYPE_CHOICES
from donate_anything.forum.tests.factories import (
    MessageFactory,
    ThreadFactory,
    UserVoteFactory,
)


class Command(BaseCommand):
    help = (
        "Generates test data items. Used in conjunction with"
        "core test data for generation."
    )
    requires_migrations_checks = True

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise Exception("You cannot use this command in production.")
        print("Creating Forum app data.")

        for _ in range(2):
            for thread_type, _ in THREAD_TYPE_CHOICES:
                ThreadFactory.create(type=thread_type)

        for thread in Thread.objects.all():
            MessageFactory.create_batch(randint(6, 30), thread=thread)

        for thread in Thread.objects.filter(type__gt=0):
            UserVoteFactory.create_batch(randint(10, 50), thread=thread)

        print("Finished creating Forum app data.")
