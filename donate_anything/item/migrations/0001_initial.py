# Generated by Django 3.0.8 on 2020-07-17 23:12

import django.contrib.postgres.fields
import django.contrib.postgres.indexes
import django.db.models.deletion
from django.conf import settings
from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("charity", "0001_initial"),
    ]

    operations = [
        TrigramExtension(),
        migrations.CreateModel(
            name="Item",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100, unique=True, db_index=True)),
                ("image", models.ImageField(blank=True, null=True, upload_to="")),
                ("is_appropriate", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="WantedItem",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                (
                    "charity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="charity.Charity",
                    ),
                ),
                (
                    "item",
                    models.ForeignKey(
                        db_index=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="item.Item",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProposedItem",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                (
                    "item",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.BigIntegerField(), size=10000, default=list
                    ),
                ),
                (
                    "names",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=100),
                        size=1000,
                        default=list,
                    ),
                ),
                ("closed", models.BooleanField(default=False)),
                (
                    "entity",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="charity.Charity",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                (
                    "category",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (0, "Financial"),
                            (1, "Clothing"),
                            (2, "Kitchenware"),
                            (3, "Books and Media"),
                            (4, "Toys and Games"),
                            (5, "Art"),
                            (6, "Hygiene"),
                            (7, "Sports"),
                            (8, "Furniture"),
                            (9, "Electronics"),
                            (10, "Internal Health"),
                            (11, "School Supplies"),
                            (12, "Linen"),
                            (13, "Recyclables"),
                            (14, "Compost"),
                            (15, "Food and Liquids"),
                            (16, "Miscellaneous"),
                        ]
                    ),
                ),
                (
                    "charity",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="charity.Charity",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="item",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["name"],
                name="item_name_sim_gin_index",
                opclasses=("gin_trgm_ops",),
            ),
        ),
        migrations.AddIndex(
            model_name="wanteditem",
            index=django.contrib.postgres.indexes.BrinIndex(
                fields=["item"], name="item_wanted_item_id_b5f5d9_brin"
            ),
        ),
        migrations.AddConstraint(
            model_name="category",
            constraint=models.UniqueConstraint(
                fields=("charity", "category"), name="charity_supports_category"
            ),
        ),
        migrations.AddConstraint(
            model_name="wanteditem",
            constraint=models.UniqueConstraint(
                fields=("charity", "item"), name="charity_need_item"
            ),
        ),
    ]
