import pytest
from django.urls import resolve, reverse

from donate_anything.users.models import User


pytestmark = pytest.mark.django_db


def test_detail(user: User):
    assert (
        reverse("users:detail", kwargs={"username": user.username})
        == f"/users/{user.username}/"
    )
    assert resolve(f"/users/{user.username}/").view_name == "users:detail"


def test_update():
    assert reverse("users:update") == "/users/~update/"
    assert resolve("/users/~update/").view_name == "users:update"


def test_redirect():
    assert reverse("users:redirect") == "/users/~redirect/"
    assert resolve("/users/~redirect/").view_name == "users:redirect"


def test_locked_out():
    assert reverse("users:person-throttled") == "/users/~locked-out/"
    assert resolve("/users/~locked-out/").view_name == "users:person-throttled"


def test_ses_bounce():
    assert reverse("users:ses-bounce") == "/users/~ses/bounce/"
    assert resolve("/users/~ses/bounce/").view_name == "users:ses-bounce"
