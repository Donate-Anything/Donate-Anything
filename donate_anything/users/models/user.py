from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Default user for Donate Anything.
    """

    id = models.BigAutoField(_("ID"), primary_key=True)

    email = models.EmailField(_("email address"))
    #: First and last name do not cover name patterns around the globe
    name = models.CharField(_("Name of User"), blank=True, max_length=255)

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})


class BlacklistedEmail(models.Model):
    email = models.EmailField(primary_key=True)
