from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings

# Create your models here.
LOTTERY_CHOICES = [
    ('lotofacil', 'Lotofácil'),
    ('diadesorte', 'Dia de Sorte'),
    ('megasena', 'Mega Sena')
]


class Lottery(models.Model):
    name = models.CharField(max_length=50, choices=LOTTERY_CHOICES)
    numbersRangeLimit = models.IntegerField(default=0)
    possiblesChoicesRange = ArrayField(models.IntegerField())
    possiblesPointsToEarn = ArrayField(models.IntegerField())
    possiblesPricesRange = ArrayField(models.FloatField())
    urlHistoricResultAPI = models.URLField(max_length=500)
    urlDailyResultAPI = models.URLField(max_length=500)

    def __str__(self):
        return self.name


class Draw(models.Model):
    lottery = models.ForeignKey(Lottery, on_delete=models.CASCADE)
    number = models.IntegerField(default=1)
    date = models.DateField()
    result = ArrayField(models.IntegerField())
    nWinnersByRange = ArrayField(models.IntegerField())
    prizesInfoByRange = ArrayField(models.TextField())
    earnedValue = models.FloatField()
    nextDrawEstimatedPrize = models.FloatField()
    nextDrawAccumulatedPrize = models.FloatField()
    drawHasAccumulated = models.BooleanField()

    def __str__(self):
        return self.lottery.name + '_' + str(self.number)


class Game(models.Model):
    arrayNumbers = ArrayField(models.IntegerField())
    lottery = models.ForeignKey(
        Lottery,
        on_delete=models.CASCADE,
    )



class GamesGroup(models.Model):
    name = models.CharField(max_length=200)
    games = models.ManyToManyField(
        Game,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    lottery = models.ForeignKey(
        Lottery,
        on_delete=models.CASCADE,
    )




