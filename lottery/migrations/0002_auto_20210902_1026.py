# Generated by Django 3.2.7 on 2021-09-02 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lottery", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="lottery",
            name="numbersRange",
        ),
        migrations.RemoveField(
            model_name="lottery",
            name="possiblesChoicesRange",
        ),
        migrations.AddField(
            model_name="lottery",
            name="numbersRangeLimit",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="lottery",
            name="possiblesChoicesRangeLimit",
            field=models.IntegerField(default=0),
        ),
    ]
