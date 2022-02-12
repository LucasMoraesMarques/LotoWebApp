# Generated by Django 3.2.7 on 2022-02-12 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lottery', '0031_lottery_combs_sizes'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='combinations',
            index=models.Index(fields=['n', 'numbers'], name='combination_n_8f8147_idx'),
        ),
    ]
