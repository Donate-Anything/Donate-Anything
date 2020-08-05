from django.contrib import admin

from .models import Category, Item, ProposedItem, WantedItem


admin.site.register(Category)
admin.site.register(Item)
admin.site.register(WantedItem)
admin.site.register(ProposedItem)
