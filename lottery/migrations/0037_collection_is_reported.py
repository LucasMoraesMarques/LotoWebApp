# Generated by Django 3.2.7 on 2022-03-02 13:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lottery', '0036_alter_result_report_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='is_reported',
            field=models.BooleanField(default=False),
        ),
    ]
