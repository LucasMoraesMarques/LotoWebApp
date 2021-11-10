# Generated by Django 3.2.7 on 2021-11-08 22:34

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('lottery', '0010_auto_20211108_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='createdAt',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 8, 22, 34, 53, 467067, tzinfo=utc)),
        ),
        migrations.AddField(
            model_name='collection',
            name='updateAt',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='gameset',
            name='createdAt',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 8, 22, 34, 53, 465070, tzinfo=utc)),
        ),
        migrations.AddField(
            model_name='gameset',
            name='updateAt',
            field=models.DateTimeField(auto_now=True),
        ),
    ]