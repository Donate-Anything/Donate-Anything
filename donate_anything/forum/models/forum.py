from django.conf import settings
from django.db import models


# All votes are overridable
THREAD_TYPE_CHOICES = (
    (0, "General Message"),
    (1, "Organization Application"),  # # 80% majority, vote. Staff or verified merge.
    (2, "Business Application"),  # 80% majority vote. Staff or verified merge.
    (3, "Entity Suggested Edit"),  # 80% majority vote. Staff or verified merge.
    (4, "Adding/Removing Items"),  # 6/10 regular votes including 2 staff votes
)

VOTABLE_THREADS = (1, 2, 3, 4)


class Thread(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    type = models.PositiveSmallIntegerField(choices=THREAD_TYPE_CHOICES)
    views = models.BigIntegerField(default=0)
    # They will always show in the forum, but this just makes sure a merge happened
    accepted = models.BooleanField(default=False)
    extra = models.JSONField(default=dict)
    """
    Reserved spaces in extra jsonb:
    - OP_id: the original poster's pk as User instance (1-4)
    - entity_id: Entity's ID (4)
    - proposed_item_id: id of ProposedItem (4)
    """

    def __str__(self):
        return self.title

    @property
    def is_votable_thread(self) -> bool:
        return self.type in VOTABLE_THREADS


class Message(models.Model):
    """A message in a thread is a simple message. Nothing special."""

    id = models.BigAutoField(primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField(max_length=5000)
