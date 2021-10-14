from django.contrib import admin
from lottery.models import *

# Register your models here.


@admin.register(Lottery)
class LotteryAdmin(admin.ModelAdmin):
    pass


@admin.register(Draw)
class DrawAdmin(admin.ModelAdmin):
    pass


@admin.register(Game)
class GamesAdmin(admin.ModelAdmin):
    pass


@admin.register(GamesGroup)
class GamesGroupAdmin(admin.ModelAdmin):
    pass
