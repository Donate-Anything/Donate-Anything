from django.conf import settings
from django.db import models


VOTE_CHOICES = (
    (True, "Upvote"),
    (False, "Downvote"),
)


class UserVote(models.Model):
    id = models.BigAutoField(primary_key=True)
    thread = models.ForeignKey("forum.Thread", on_delete=models.CASCADE)
    direction = models.BooleanField(choices=VOTE_CHOICES)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
