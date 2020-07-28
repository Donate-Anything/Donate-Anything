from django.urls import path

from donate_anything.forum.views import list


app_name = "forum"
urlpatterns = [
    path("", list.forum_view, name="home"),
    path("<int:thread>/", list.thread_view, name="thread"),
    path("<int:thread>/post/", list.thread_form_view, name="thread-form"),
]
