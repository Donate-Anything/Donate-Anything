from django.urls import path

from donate_anything.charity.views import organization


app_name = "charity"
urlpatterns = [path("<int:pk>/", organization, name="organization")]
