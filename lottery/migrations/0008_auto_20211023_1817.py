# Generated by Django 3.2.7 on 2021-10-23 21:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('lottery', '0007_game_gamesgroup'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name': 'Gameset Collection',
                'verbose_name_plural': 'Gameset Collections',
                'db_table': 'collections',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Gameset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'verbose_name': 'Gameset',
                'verbose_name_plural': 'Gamesets',
                'db_table': 'gamesets',
                'ordering': ['name'],
            },
        ),
        migrations.AlterModelOptions(
            name='draw',
            options={'ordering': ['number'], 'verbose_name': 'Lottery Draw', 'verbose_name_plural': 'Lottery Draws'},
        ),
        migrations.AlterModelOptions(
            name='game',
            options={'ordering': ['lottery'], 'verbose_name': 'Lottery Game', 'verbose_name_plural': 'Lottery Games'},
        ),
        migrations.AlterField(
            model_name='draw',
            name='date',
            field=models.DateField(verbose_name='Date draw occurred'),
        ),
        migrations.AlterField(
            model_name='draw',
            name='drawHasAccumulated',
            field=models.BooleanField(verbose_name='If draw has no winners'),
        ),
        migrations.AlterField(
            model_name='draw',
            name='earnedValue',
            field=models.FloatField(verbose_name='Earned money from bets'),
        ),
        migrations.AlterField(
            model_name='draw',
            name='lottery',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lottery.lottery', verbose_name='Lottery type'),
        ),
        migrations.AlterField(
            model_name='draw',
            name='nextDrawAccumulatedPrize',
            field=models.FloatField(verbose_name='Prize accumulated for next draw'),
        ),
        migrations.AlterField(
            model_name='draw',
            name='nextDrawEstimatedPrize',
            field=models.FloatField(verbose_name='Prize estimated for next draw'),
        ),
        migrations.AlterField(
            model_name='draw',
            name='number',
            field=models.IntegerField(default=1, verbose_name='Draw unique identifier'),
        ),
        migrations.AlterField(
            model_name='game',
            name='lottery',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lottery.lottery', verbose_name='Lottery type'),
        ),
        migrations.AlterField(
            model_name='lottery',
            name='numbersRangeLimit',
            field=models.IntegerField(default=0, verbose_name='Range of numbers start in 0 and finish in'),
        ),
        migrations.AlterModelTable(
            name='draw',
            table='draws',
        ),
        migrations.AlterModelTable(
            name='game',
            table='games',
        ),
        migrations.AlterModelTable(
            name='lottery',
            table='lottery',
        ),
        migrations.DeleteModel(
            name='GamesGroup',
        ),
        migrations.AddField(
            model_name='gameset',
            name='games',
            field=models.ManyToManyField(related_name='gamesets', to='lottery.Game', verbose_name='Games included'),
        ),
        migrations.AddField(
            model_name='gameset',
            name='lottery',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gamesets', to='lottery.lottery', verbose_name='Lottery type'),
        ),
        migrations.AddField(
            model_name='gameset',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gamesets', to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
        migrations.AddField(
            model_name='collection',
            name='gamesets',
            field=models.ManyToManyField(related_name='collections', to='lottery.Gameset', verbose_name='Gamesets included'),
        ),
        migrations.AddField(
            model_name='collection',
            name='lottery',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collections', to='lottery.lottery', verbose_name='Lottery type'),
        ),
        migrations.AddField(
            model_name='collection',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collections', to=settings.AUTH_USER_MODEL, verbose_name='Owner'),
        ),
    ]
