# Generated by Django 3.2.7 on 2022-02-12 13:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lottery', '0029_combinations'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='combinations',
            options={'ordering': ['n'], 'verbose_name': 'N-uplas combinations', 'verbose_name_plural': 'N-uplas combinations'},
        ),
        migrations.AlterModelTable(
            name='combinations',
            table='combinations',
        ),
    ]
