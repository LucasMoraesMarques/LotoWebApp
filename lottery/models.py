import math

from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.utils import timezone
# Create your models here.
LOTTERY_CHOICES = [
    ("lotofacil", "Lotofácil"),
    ("diadesorte", "Dia de Sorte"),
    ("megasena", "Mega Sena"),
]


class GameParity(models.TextChoices):
    ODD = "odd", "Ímpar"
    EVEN = "even", "Par"
    NEUTRAL = "neutral", "Neutro"


class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None


class Lottery(models.Model):
    name = models.CharField(max_length=50, choices=LOTTERY_CHOICES)
    numbersRangeLimit = models.IntegerField("Range of numbers start in 0 and finish in",default=0)
    possiblesChoicesRange = ArrayField(models.IntegerField())
    possiblesPointsToEarn = ArrayField(models.IntegerField())
    possiblesPricesRange = ArrayField(models.FloatField())
    urlHistoricResultAPI = models.URLField(max_length=500)
    urlDailyResultAPI = models.URLField(max_length=500)
    combs_sizes = ArrayField(models.IntegerField(), default=[])
    last_draw_number = models.IntegerField(default=0)

    class Meta:
        db_table = 'lottery'

    def __str__(self):
        return self.name

    @property
    def choices_description(self):
        return f"{self.possiblesChoicesRange[0]} a {self.possiblesChoicesRange[-1]}"

    @property
    def points_description(self):
        return f"{self.possiblesPointsToEarn[0]} a {self.possiblesPointsToEarn[-1]}"

    @property
    def probability_of_earn(self):
        return math.comb(self.numbersRangeLimit, self.possiblesChoicesRange[0])


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
    sum = models.IntegerField(default=0)
    max_seq = models.IntegerField(default=-1)
    min_seq = models.IntegerField(default=-1)
    max_gap = models.IntegerField(default=-1)
    n_primes = models.IntegerField(default=-1)
    parity = models.CharField(choices=GameParity.choices, default=GameParity.NEUTRAL, max_length=128)

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
    max_seq = models.IntegerField(default=-1)
    min_seq = models.IntegerField(default=-1)
    max_gap = models.IntegerField(default=-1)
    n_primes = models.IntegerField(default=-1)
    parity = models.CharField(choices=GameParity.choices, default=GameParity.NEUTRAL, max_length=128)

    class Meta:
        ordering = ['lottery']
        db_table = 'games'
        verbose_name = 'Lottery Game'
        verbose_name_plural = 'Lottery Games'
        indexes = [models.Index(fields=["arrayNumbers"])]

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


class Combinations(models.Model):
    lottery = models.ForeignKey(
        Lottery,
        on_delete=models.CASCADE,
        related_name="combinations",
        verbose_name="N-uplas Combinations"
    )
    n = models.IntegerField(default=0)
    repetitions = models.IntegerField(default=0)
    numbers = ArrayField(models.IntegerField())

    class Meta:
        ordering = ['n']
        db_table = 'combinations'
        verbose_name = 'N-uplas combinations'
        verbose_name_plural = 'N-uplas combinations'
        indexes = [models.Index(fields=["n", "numbers"])]


class Result(models.Model):
    lottery = models.ForeignKey(
        Lottery,
        on_delete=models.CASCADE,
        related_name="generated_results",
        verbose_name="Generated Results"
    )
    collection = models.ForeignKey(
        Collection,
        on_delete=models.CASCADE,
        related_name="results",
        verbose_name="Collection results"
    )
    number_of_game_sets = models.IntegerField(default=0)
    number_of_games = models.IntegerField(default=0)
    draw = models.ForeignKey(
        Draw,
        on_delete=models.CASCADE,
        related_name="collections_results",
        verbose_name="Collection result in draw"
    )
    points_info = ArrayField(models.JSONField(null=True), null=True)
    price = models.FloatField(default=0)
    prizes = models.FloatField(default=0)
    balance = models.FloatField(default=0)
    abridged = models.BooleanField(default=True)

    class Meta:
        db_table = 'results'
        verbose_name = 'Collections Result'
        verbose_name_plural = 'Collections Results'

