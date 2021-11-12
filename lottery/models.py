from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.conf import settings
from django.utils import timezone
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
    lottery = models.ForeignKey(Lottery, on_delete=models.CASCADE, verbose_name='Lottery', related_name='draws')
    number = models.IntegerField('Draw number', default=1)
    date = models.DateField('Draw date')
    result = ArrayField(models.IntegerField())
    extraResultField = models.CharField(max_length=100, null=True)
    metadata = ArrayField(models.JSONField(null=True, default=dict), null=True)
    prizesInfoByRange = ArrayField(models.JSONField(null=True), null=True)
    maxPrize = models.FloatField('Max prize', null=True)
    earnedValue = models.FloatField('Earned money from bets')
    nextDrawEstimatedPrize = models.FloatField('Prize estimated for next draw')
    nextDrawAccumulatedPrize = models.FloatField('Prize accumulated for next draw')
    hasAccumulated = models.BooleanField('Draw had winners?')

    class Meta:
        ordering = ['number']
        db_table = 'draws'
        verbose_name = 'Draw'
        verbose_name_plural = 'Draws'

    def __str__(self):
        return self.lottery.name + "_" + str(self.number)


class Game(models.Model):
    arrayNumbers = ArrayField(models.IntegerField())
    lottery = models.ForeignKey(
        Lottery,
        on_delete=models.CASCADE,
        verbose_name='Lottery type'
    )
    sum = models.IntegerField(default=0)
    gameCode = models.BigIntegerField(default=0)

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

    numberOfGames = models.IntegerField(default=0)
    gameLength = models.IntegerField(default=0)
    isActive = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)
    updateAt = models.DateTimeField(auto_now=True)

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

    numberOfGames = models.IntegerField(default=0)
    numberOfGamesets = models.IntegerField(default=0)
    createdAt = models.DateTimeField(auto_now_add=True)
    updateAt = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        db_table = 'collections'
        verbose_name = 'Gameset Collection'
        verbose_name_plural = 'Gameset Collections'
