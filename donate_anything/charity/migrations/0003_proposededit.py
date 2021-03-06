# Generated by Django 3.0.8 on 2020-07-28 18:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("charity", "0002_application"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProposedEdit",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("commit_message", models.TextField(max_length=300)),
                ("link", models.URLField(blank=True, null=True)),
                (
                    "description",
                    models.TextField(blank=True, max_length=1000, null=True),
                ),
                (
                    "how_to_donate",
                    models.TextField(blank=True, max_length=300, null=True),
                ),
                (
                    "entity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="charity.Charity",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
