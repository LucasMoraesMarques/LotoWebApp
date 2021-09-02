# Generated by Django 3.2.7 on 2021-09-02 16:32

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lottery', '0006_alter_draw_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('arrayNumbers', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=None)),
                ('lottery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lottery.lottery')),
            ],
        ),
        migrations.CreateModel(
            name='GamesGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('games', models.ManyToManyField(to='lottery.Game')),
                ('lottery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lottery.lottery')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
