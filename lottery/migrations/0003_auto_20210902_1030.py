# Generated by Django 3.2.7 on 2021-09-02 13:30

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lottery", "0002_auto_20210902_1026"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="lottery",
            name="possiblesChoicesRangeLimit",
        ),
        migrations.AddField(
            model_name="lottery",
            name="possiblesChoicesRange",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.IntegerField(), size=None
            ),
            preserve_default=False,
        ),
    ]
