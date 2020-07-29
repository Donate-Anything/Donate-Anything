from allauth.account.forms import LoginForm
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import forms, get_user_model
from django.core.exceptions import ValidationError
from django.forms import EmailField, Form
from django.utils.translation import gettext_lazy as _


User = get_user_model()


class UserChangeForm(forms.UserChangeForm):
    class Meta(forms.UserChangeForm.Meta):
        model = User


class UserCreationForm(forms.UserCreationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    error_message = forms.UserCreationForm.error_messages.update(
        {"duplicate_username": _("This username has already been taken.")}
    )

    class Meta(forms.UserCreationForm.Meta):
        model = User
        # Require email since we're going to have a Points system
        fields = (
            "email",
            "username",
        )
        field_classes = {"email": EmailField}

    def clean_username(self):
        username = self.cleaned_data["username"]

        if User.objects.filter(username=username).exists():
            raise ValidationError(self.error_messages["duplicate_username"])
        else:
            return username


class ReCAPTCHAAdminAuthenticationForm(AdminAuthenticationForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)


class AxesLoginForm(LoginForm):
    """Extended login form class that supplied the
    user credentials for Axes compatibility.
    """

    def user_credentials(self):
        credentials = super().user_credentials()
        credentials["login"] = credentials.get("email") or credentials.get("username")
        return credentials


class AxesLockoutCaptchaForm(Form):
    captcha = ReCaptchaField()
