import os
import django
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LotoWebApp.settings")
django.setup()
from lottery.models import Game

LOTTERY_CHOICES = {"lotofacil": 1, "diadesorte": 2, "megasena": 3}


def populate(model, data=0, lottery=0, id=0):
    games = model.objects.all()
    #model.objects.create(lottery_id=LOTTERY_CHOICES[lottery], arrayNumbers=data, id=id)
    for game in games.order_by('id'):
        sumNumbers = sum(game.arrayNumbers)
        game.sum = sumNumbers
        game.save(update_fields=['sum'])



if __name__ == "__main__":
    """jogos = pd.read_csv("todosjogosloto.csv", index_col=None, header=None)
    for index, jogo in jogos.iterrows():
        jogo = jogo.to_list()
        populate(Game, jogo, "lotofacil", id=index)"""
    populate(Game)
