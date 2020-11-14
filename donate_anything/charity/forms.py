from typing import Union

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from donate_anything.charity.models import (
    BusinessApplication,
    Charity,
    OrganizationApplication,
    ProposedEdit,
)


# Be explicit in case of added fields
_default_application_fields = [
    "name",
    "link",
    "description",
    "how_to_donate",
    "specific_destination",
]

_default_help_texts = {
    "name": _("Organization Name"),
    "link": _(
        "This is the link to your website/domain. Social media "
        "platforms are acceptable if the community finds it permissible."
    ),
    "description": _(
        "Description of your organization. Specify what its role is in a problem, "
        "what you do in general, and a SMALL gist of why you're helping."
    ),
    "how_to_donate": _("Specify how people can donate the items you will fulfill."),
    "specific_destination": _(
        "Who/what is receiving these donations or where are they going?"
    ),
}


class MDWidget(forms.Textarea):
    template_name = "widgets/markdown_editor.html"


_default_widgets = {
    "description": MDWidget(),
    "how_to_donate": MDWidget(),
}


class OrganizationForm(forms.ModelForm):
    social_media = forms.URLField(
        required=False,
        help_text=_(
            "If you have a social media post about your application, "
            "please paste the link to it here. This may help the "
            "community better understand YOUR community."
        ),
    )

    class Meta:
        model = OrganizationApplication
        fields = _default_application_fields + ["chapter_filing"]
        help_texts = {
            **_default_help_texts,
            "chapter_filing": _(
                "Proof via your government's websites (e.g. IRS in "
                "the U.S.) that your organization is a valid entity. "
                "This MUST be public information. Preferably a link. "
                "If it is an image, upload it to an image hosting website."
            ),
        }
        widgets = {
            **_default_widgets,
            "chapter_filing": MDWidget(),
        }

    def __init__(self, *args, **kwargs):
        self.applier = kwargs.pop("user", None)
        self.social_media_value = None
        super(OrganizationForm, self).__init__(*args, **kwargs)

    def save(self, commit=True, create_proposed=True):
        instance = super(OrganizationForm, self).save(commit=False)
        instance.applier = self.applier
        extras = {}
        if self.social_media_value not in ("", None):
            extras["social_media"] = self.social_media_value
        instance.extra = extras
        if commit:
            instance.save()
        return instance

    def clean_social_media(self):
        self.social_media_value = self.cleaned_data.get("social_media", "")


class BusinessForm(forms.ModelForm):
    class Meta:
        model = BusinessApplication
        fields = _default_application_fields + [
            "years_of_service",
            "reason",
            "type_of_business",
        ]
        help_texts = {
            **_default_help_texts,
            "years_of_service": _(
                "The number of years your business has been operating."
            ),
            "reason": _(
                "What is the reason for starting these accepting "
                "donations? For example, a recycling company would "
                "simply say for saving the planet by reducing waste."
            ),
            "type_of_business": _("What type of business are you?"),
        }
        widgets = _default_widgets

    def __init__(self, *args, **kwargs):
        self.applier = kwargs.pop("user", None)
        super(BusinessForm, self).__init__(*args, **kwargs)

    def save(self, commit=True, create_proposed=True):
        instance = super(BusinessForm, self).save(commit=False)
        instance.applier = self.applier
        if commit:
            instance.save()
        return instance


class SuggestedEditForm(forms.Form):
    """If create is True, id is entity ID.
    Else, it's the suggested edit's ID.
    """

    id = forms.IntegerField(widget=forms.HiddenInput())
    edit = forms.CharField(
        label="Suggest in Markdown", widget=MDWidget(), max_length=5000
    )
    # Not sure why this can't be BooleanField...
    create = forms.CharField(widget=forms.HiddenInput())


class ExistingSuggestEditForm(forms.ModelForm):
    """Suggesting edits for active/existing organizations in the db"""

    class Meta:
        model = ProposedEdit
        fields = [
            "link",
            "description",
            "how_to_donate",
            "commit_message",
        ]
        widgets = {
            **_default_widgets,
            "commit_message": MDWidget(),
        }
        help_texts = {
            "commit_message": _("A commit message is your justification for this edit.")
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.entity: Union[int, Charity] = kwargs.pop("entity", None)
        self.is_verified = kwargs.pop("is_verified", False)
        super(ExistingSuggestEditForm, self).__init__(*args, **kwargs)
        if self.is_verified:
            self.fields["logo"] = forms.ImageField(
                widget=forms.ClearableFileInput(), required=False
            )

    def clean(self):
        cleaned_data = super(ExistingSuggestEditForm, self).clean()
        if type(self.entity) == int:
            self.entity = Charity.objects.get(id=self.entity)
        fields = ("description", "link", "how_to_donate")
        if self.is_verified:
            fields += ("logo",)
        for field in fields:
            if cleaned_data[field] not in (getattr(self.entity, field), None, ""):
                break
        else:
            print(getattr(self.entity, "logo"))
            print(cleaned_data.get("logo"))
            raise ValidationError(
                _(f"One of the fields must be filled out: {', '.join(fields)}.")
            )
        return cleaned_data

    def save(self, commit=True):
        instance = super(ExistingSuggestEditForm, self).save(commit=False)
        instance.user = self.user
        instance.entity = self.entity
        if commit:
            instance.save()
        return instance
