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


@admin.register(Gameset)
class GamesetAdmin(admin.ModelAdmin):
    model = Gameset
    verbose_name = "Gamesets"
    list_display = ('name', 'user', 'lottery', 'isActive')
    raw_id_fields = ('games',)


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    model = Collection
    verbose_name = "Collection"
    list_display = ('name', 'user', 'lottery', 'createdAt')
    raw_id_fields = ('gamesets',)

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    readonly_fields = ("draw",)