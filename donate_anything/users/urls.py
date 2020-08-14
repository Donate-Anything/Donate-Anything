from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django_ses.views import handle_bounce

from donate_anything.users.views import (
    locked_out,
    user_detail_view,
    user_redirect_view,
    user_update_view,
)


app_name = "users"
urlpatterns = [
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("~locked-out/", view=locked_out, name="person-throttled"),
    path("~ses/bounce/", csrf_exempt(handle_bounce), name="ses-bounce"),
    path("<str:username>/", view=user_detail_view, name="detail"),
]
