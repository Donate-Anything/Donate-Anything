from django.contrib import admin, messages
from django.utils.translation import ngettext

from donate_anything.item.models import Category, Item, ProposedItem, WantedItem
from donate_anything.item.utils.merge_proposed_to_active import merge


admin.site.register(Category)
admin.site.register(Item)
admin.site.register(WantedItem)


class ProposedItemAdmin(admin.ModelAdmin):
    actions = ["merge_items"]
    list_display = ("get_entity_name", "get_username", "closed")
    list_select_related = ["entity", "user"]

    def get_username(self, obj):
        return obj.user.username

    get_username.short_description = "Username"

    def get_entity_name(self, obj):
        return obj.entity.name

    get_entity_name.short_description = "Entity Name"

    def merge_items(self, request, queryset):
        for proposed in queryset:
            merge(proposed.entity, proposed)
        self.message_user(
            request,
            ngettext(
                "%d ProposedItem was merged",
                "%d ProposedItems were merged",
                len(queryset),
            )
            % len(queryset),
            messages.SUCCESS,
        )


admin.site.register(ProposedItem, ProposedItemAdmin)
