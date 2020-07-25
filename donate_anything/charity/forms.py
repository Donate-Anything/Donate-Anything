from django import forms
from django.utils.translation import gettext_lazy as _

from donate_anything.charity.models.apply import (
    BusinessApplication,
    OrganizationApplication,
    ProposedBusinessItem,
    ProposedOrganizationItem,
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
            if create_proposed:
                ProposedOrganizationItem.objects.create(entity=instance, item=[])
        return instance

    def clean_social_media(self):
        self.social_media_value = self.cleaned_data["social_media"]


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
            if create_proposed:
                ProposedBusinessItem.objects.create(entity=instance, item=[])
        return instance
