from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from donate_anything.users import models
from donate_anything.users.forms import (
    ReCAPTCHAAdminAuthenticationForm,
    UserChangeForm,
    UserCreationForm,
)


User = get_user_model()

admin.site.login_form = ReCAPTCHAAdminAuthenticationForm
admin.site.login_template = "admin/login_recaptcha.html"


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (("User", {"fields": ("name",)}),) + auth_admin.UserAdmin.fieldsets
    list_display = ["username", "name", "is_superuser"]
    search_fields = ["name"]


admin.site.register(models.BanReason)
admin.site.register(models.Report)
admin.site.register(models.BlacklistedEmail)
