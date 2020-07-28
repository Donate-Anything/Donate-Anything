from django.contrib import admin

from . import models


admin.site.register(models.Charity)

admin.site.register(models.OrganizationApplication)
admin.site.register(models.BusinessApplication)
admin.site.register(models.AppliedBusinessEdit)
admin.site.register(models.AppliedOrganizationEdit)
