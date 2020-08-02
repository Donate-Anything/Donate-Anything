from typing import List, Type

from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from django.utils.translation import gettext_lazy as _

from donate_anything.charity.models import Charity
from donate_anything.item.models import Item


class ModifyItemsForm(forms.Form):
    """Form for ADDING new items and names for an org.
    """

    id = forms.IntegerField(min_value=1, max_value=9223372036854775807, required=False)
    entity = forms.IntegerField(
        min_value=1, max_value=9223372036854775807, required=False
    )
    item = SimpleArrayField(
        forms.IntegerField(min_value=1, max_value=9223372036854775807),
        max_length=10000,
        required=False,
    )
    # TODO Add delete. I'm just scared that automating deletes can be devastating in bot attacks
    names = SimpleArrayField(
        forms.CharField(max_length=100), max_length=1000, required=False
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
        return names

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
