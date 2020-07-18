from django.urls import path

from donate_anything.item import views


app_name = "item"
urlpatterns = [
    path(
        "api/v1/item-autocomplete/",
        views.search_item_autocomplete,
        name="item-autocomplete",
    ),
    path(
        "api/v1/category/<int:category_type>/",
        views.search_category,
        name="category-filter",
    ),
    path("lookup/<int:pk>/", views.search_item, name="lookup-item"),
    path("multi-lookup/", views.search_multiple_items, name="lookup-multi-item"),
]
