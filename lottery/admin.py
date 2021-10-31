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
class GamesGroupAdmin(admin.ModelAdmin):
    model = Gameset
    verbose_name = "Gamesets"
    list_display = ('name', 'user', 'lottery')
    raw_id_fields = ('games',)


@admin.register(Collection)
class GamesGroupAdmin(admin.ModelAdmin):
    model = Collection
    verbose_name = "Collection"
    list_display = ('name', 'user', 'lottery')
    raw_id_fields = ('gamesets',)