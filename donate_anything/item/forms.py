from typing import List, Type

from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _

from donate_anything.charity.models import Charity
from donate_anything.item.models.item import WANTED_ITEM_CONDITIONS, Item


_max_condition_value = WANTED_ITEM_CONDITIONS[-1][0]


class ModifyItemsForm(forms.Form):
    """Form for ADDING new items and names for an org."""

    id = forms.IntegerField(min_value=1, max_value=9223372036854775807, required=False)
    entity = forms.IntegerField(
        min_value=1, max_value=9223372036854775807, required=False
    )
    item = SimpleArrayField(
        forms.IntegerField(min_value=1, max_value=9223372036854775807),
        max_length=20000,
        required=False,
    )
    item_condition = SimpleArrayField(
        forms.IntegerField(min_value=0, max_value=_max_condition_value),
        max_length=20000,
        required=False,
    )
    # TODO Add delete. I'm just scared that automating deletes can be devastating in bot attacks
    names = SimpleArrayField(
        forms.CharField(max_length=100), max_length=1500, required=False
    )
    names_condition = SimpleArrayField(
        forms.IntegerField(min_value=0, max_value=_max_condition_value),
        max_length=1500,
        required=False,
    )

    def clean_item(self):
        item: List[int] = self.cleaned_data["item"]
        if item is []:
            item: Type[list] = list
        else:
            if Item.objects.filter(id__in=item, is_appropriate=False).exists():
                raise forms.ValidationError(_("You can only select appropriate items."))
        return item

    def clean_names(self):
        names = self.cleaned_data["names"]
        if names is []:
            names = list
        else:
            names = [escape(name) for name in names]
        return names

    def clean(self):
        cleaned_data = super().clean()
        try:
            item: List[int] = self.cleaned_data["item"]
            item_error = forms.ValidationError(
                "Item list and conditions for them are not equal in size."
            )
            if item is []:
                if len(self.cleaned_data["item_condition"]) != 0:
                    self.add_error("item", item_error)
                    self.add_error("item_condition", item_error)
            else:
                if len(self.cleaned_data["item_condition"]) != len(item):
                    self.add_error("item", item_error)
                    self.add_error("item_condition", item_error)
        except KeyError:
            # In case item is just left null
            pass
        try:
            names = self.cleaned_data["names"]
            names_error = forms.ValidationError(
                "Name list and conditions for them are not equal in size."
            )
            if names is []:
                if len(self.cleaned_data["names_condition"]) != 0:
                    self.add_error("names", names_error)
                    self.add_error("names_condition", names_error)
            else:
                if len(self.cleaned_data["names_condition"]) != len(names):
                    self.add_error("names", names_error)
                    self.add_error("names_condition", names_error)
        except KeyError:
            # In case item is just left null
            pass
        return cleaned_data

    def clean_entity(self):
        entity = self.cleaned_data["entity"]
        if entity is None and self.cleaned_data["id"] is None:
            raise forms.ValidationError(
                _(
                    "You must specify either the id of your form "
                    "or the entity's id to create a new form."
                )
            )
        if entity is not None:
            if not Charity.objects.filter(id=entity).exists():
                raise forms.ValidationError(_("Entity with that ID does not exist."))
        return entity
