from django.urls import path
from django.views.generic import TemplateView

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
    # Item List
    path("list/<int:entity_id>/", views.list_org_items_view, name="list-item-template"),
    path(
        "api/v1/list/<int:charity_id>/",
        views.list_active_entity_items,
        name="list-item",
    ),
    path(
        "list/proposed/<int:proposed_item_pk>/",
        views.list_org_proposed_item_view,
        name="list-proposed-template",
    ),
    path(
        "api/v1/proposed/<int:proposed_item_pk>/exist/",
        views.list_proposed_existing_item,
        name="list-proposed-item",
    ),
    path(
        "proposed/initial/",
        views.initial_proposed_item_template,
        name="initial-proposed-template",
    ),
    path("proposed/form/", views.proposed_item_form_view, name="proposed-item-form"),
]
