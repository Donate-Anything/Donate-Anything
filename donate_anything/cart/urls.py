from django.urls import path
from django.views.generic import TemplateView

from donate_anything.cart.views.search import search_view


app_name = "cart"

urlpatterns = [
    path("search/", search_view, name="search"),
    path("cart/", TemplateView.as_view(template_name="cart/cart.html"), name="cart"),
]
