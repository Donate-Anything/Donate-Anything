# Generated by Django 3.1 on 2020-08-22 19:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("charity", "0003_proposededit"),
    ]

    operations = [
        migrations.AlterField(
            model_name="charity",
            name="how_to_donate",
            field=models.TextField(max_length=1000),
        ),
        migrations.AlterField(
            model_name="proposededit",
            name="how_to_donate",
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
    ]
