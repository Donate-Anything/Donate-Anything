from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from donate_anything.users import models
from donate_anything.users.forms import ReCAPTCHAAdminAuthenticationForm, UserChangeForm


User = get_user_model()

admin.site.login_form = ReCAPTCHAAdminAuthenticationForm
admin.site.login_template = "admin/login_recaptcha.html"


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    fieldsets = (("User", {"fields": ("name",)}),) + auth_admin.UserAdmin.fieldsets
    list_display = ["username", "name", "is_superuser"]
    search_fields = (["username"],)


admin.site.register(models.BanReason)
admin.site.register(models.Report)
admin.site.register(models.BlacklistedEmail)


@admin.register(models.VerifiedAccount)
class VerifiedAccountAdmin(admin.ModelAdmin):
    search_fields = ["user__username"]
    list_select_related = ["user"]
    list_display = ("get_username", "_accepted")

    def get_username(self, obj):
        return obj.user.get_username()

    get_username.short_description = "Username"
    get_username.admin_order_field = "user__username"

    def _accepted(self, obj):
        return obj.accepted

    _accepted.short_description = "Currently Verified"
    _accepted.admin_order_field = "accepted"
    _accepted.boolean = True
