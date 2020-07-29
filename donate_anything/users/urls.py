from django.urls import path

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
    path("<str:username>/", view=user_detail_view, name="detail"),
]
