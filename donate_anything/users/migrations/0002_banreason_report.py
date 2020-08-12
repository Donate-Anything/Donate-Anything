# Generated by Django 3.0.8 on 2020-07-17 18:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BanReason",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("reason", models.TextField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name="Report",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("reason", models.TextField(max_length=300)),
                (
                    "ban",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="users.BanReason",
                    ),
                ),
            ],
        ),
    ]
