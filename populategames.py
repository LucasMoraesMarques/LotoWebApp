import os
import re

import django
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LotoWebApp.settings")
django.setup()
from lottery.models import Game

LOTTERY_CHOICES = {"lotofacil": 1, "diadesorte": 2, "megasena": 3}


def populate(model, data=0, lottery=0, id=0):
    from functools import reduce
    games = model.objects.all().order_by('id')
    #model.objects.create(lottery_id=LOTTERY_CHOICES[lottery], arrayNumbers=data, id=id)
    for game in games:
        #numbers = list(game.arrayNumbers)
        #numbers.reverse()
        #game.subtract = reduce(lambda a,b: a-b, numbers)
        #game.save(update_fields=['subtract'])
        game.gameCode = reverseMapping(game.arrayNumbers)
        game.save(update_fields=['gameCode'])

def generator2():
    inicio = 0b111111111111111
    fim = 0b1111111111111110000000000
    #inicio = 0b1111111
    #fim = 0b1111111000000000000000000000000

    jogos = []
    for i in range(inicio, fim + 1):
        iCopy = f"{i:015b}"
        if iCopy.count("1") == 15:
            x = re.split(r"([01])", iCopy)
            x = [j for j in x if j not in [""]]
            jogos.append(x)
        else:
            continue

    jogos = binaryMapping(jogos)
    return jogos


def binaryMapping(jogos):
    jogosMapped = []
    for jogo in jogos:
        a = []
        for i, j in enumerate(jogo):
            if j == '1':
                a.append(i + 1)
        jogosMapped.append(a)
    return jogosMapped



def reverseMapping(jogo):
    jogo0 = [0 for i in range(25)]
    for number in jogo:
        jogo0[number-1] = 1
    number = 0
    for pos,value in enumerate(jogo0):
        number += value*2**(pos)
    return number




if __name__ == "__main__":
    """jogos = pd.read_csv("todosjogosloto.csv", index_col=None, header=None)
    for index, jogo in jogos.iterrows():
        jogo = jogo.to_list()
        populate(Game, jogo, "lotofacil", id=index)"""
    populate(Game)
