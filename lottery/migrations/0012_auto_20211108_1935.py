# Generated by Django 3.2.7 on 2021-11-08 22:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lottery', '0011_auto_20211108_1934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='createdAt',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='gameset',
            name='createdAt',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
