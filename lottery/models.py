from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings

# Create your models here.
LOTTERY_CHOICES = [
    ("lotofacil", "Lotofácil"),
    ("diadesorte", "Dia de Sorte"),
    ("megasena", "Mega Sena"),
]


class Lottery(models.Model):
    name = models.CharField(max_length=50, choices=LOTTERY_CHOICES)
    numbersRangeLimit = models.IntegerField("Range of numbers start in 0 and finish in",default=0)
    possiblesChoicesRange = ArrayField(models.IntegerField())
    possiblesPointsToEarn = ArrayField(models.IntegerField())
    possiblesPricesRange = ArrayField(models.FloatField())
    urlHistoricResultAPI = models.URLField(max_length=500)
    urlDailyResultAPI = models.URLField(max_length=500)

    class Meta:
        db_table = 'lottery'

    def __str__(self):
        return self.name


class Draw(models.Model):
    lottery = models.ForeignKey(Lottery, on_delete=models.CASCADE, verbose_name='Lottery type')
    number = models.IntegerField('Draw unique identifier', default=1)
    date = models.DateField('Date draw occurred')
    result = ArrayField(models.IntegerField())
    nWinnersByRange = ArrayField(models.IntegerField())
    prizesInfoByRange = ArrayField(models.TextField())
    earnedValue = models.FloatField('Earned money from bets')
    nextDrawEstimatedPrize = models.FloatField('Prize estimated for next draw')
    nextDrawAccumulatedPrize = models.FloatField('Prize accumulated for next draw')
    drawHasAccumulated = models.BooleanField('If draw has no winners')

    class Meta:
        ordering = ['number']
        db_table = 'draws'
        verbose_name = 'Lottery Draw'
        verbose_name_plural = 'Lottery Draws'

    def __str__(self):
        return self.lottery.name + "_" + str(self.number)


class Game(models.Model):
    arrayNumbers = ArrayField(models.IntegerField())
    lottery = models.ForeignKey(
        Lottery,
        on_delete=models.CASCADE,
        verbose_name='Lottery type'
    )

    class Meta:
        ordering = ['lottery']
        db_table = 'games'
        verbose_name = 'Lottery Game'
        verbose_name_plural = 'Lottery Games'

    def __str__(self):
        return str(self.id)


class Gameset(models.Model):
    name = models.CharField(max_length=200)
    games = models.ManyToManyField(
        Game, related_name="gamesets", verbose_name='Games included'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='gamesets',
        verbose_name='Owner'
    )
    lottery = models.ForeignKey(
        Lottery,
        on_delete=models.CASCADE,
        related_name='gamesets',
        verbose_name='Lottery type'
    )

    class Meta:
        ordering = ['name']
        db_table = 'gamesets'
        verbose_name = 'Gameset'
        verbose_name_plural = 'Gamesets'

    def __str__(self):
        return str(self.name)


class Collection(models.Model):
    name = models.CharField(max_length=200)
    gamesets = models.ManyToManyField(
        Gameset,
        related_name='collections',
        verbose_name='Gamesets included'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='collections',
        verbose_name='Owner'
    )

    lottery = models.ForeignKey(
        Lottery,
        on_delete=models.CASCADE,
        related_name='collections',
        verbose_name='Lottery type'
    )

    class Meta:
        ordering = ['name']
        db_table = 'collections'
        verbose_name = 'Gameset Collection'
        verbose_name_plural = 'Gameset Collections'
