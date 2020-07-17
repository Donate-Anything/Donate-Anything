from django.db import models


class BanReason(models.Model):
    id = models.BigAutoField(primary_key=True)
    reason = models.TextField(max_length=500)


class Report(models.Model):
    id = models.BigAutoField(primary_key=True)
    reason = models.TextField(max_length=300)
    ban = models.ForeignKey(BanReason, on_delete=models.SET_NULL, null=True, blank=True)
