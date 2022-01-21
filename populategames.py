import os
import re

import django
import pandas as pd
import numpy as np
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LotoWebApp.settings")
django.setup()
from lottery.models import Game, Draw

LOTTERY_CHOICES = {"lotofacil": 1, "diadesorte": 2, "megasena": 3}


def populate_game_code():
    games = Game.objects.all().order_by('id')
    for game in games:
        game.gameCode = reverseMapping(game.arrayNumbers)
        game.save(update_fields=['gameCode'])


def populate_games():
    jogos = pd.read_pickle("megaFiltered.csv")
    print(jogos.head())
    print(len(jogos))
    for index, jogo in jogos.iterrows():
        numbers = jogo[:6].to_list()
        isOdd = jogo["isOdd"]
        nPrime = jogo["nPrime"]
        maxGap = jogo["maxGap"]
        maxSeq = jogo["maxSeq"]
        minSeq = jogo["minSeq"]
        gamecode = reverseMapping(numbers)
        Game.objects.create(
            lottery_id=3,
            id=5898361 +index,
            arrayNumbers=numbers,
            max_seq=maxSeq,
            min_seq=minSeq,
            max_gap=maxGap,
            n_primes=nPrime,
            is_odd=isOdd,
            sum=sum(numbers),
            gameCode=gamecode
        )





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
    jogo0 = [0 for i in range(60)]
    for number in jogo:
        jogo0[number-1] = 1
    number = 0
    for pos,value in enumerate(jogo0):
        number += value*2**(pos)
    return number


def isOdd(jogo):
    """Checa se um jogo é majoritariamente par ou ímpar

    :param jogo: Jogo único
    :return: Retorna True se o jogo é predominantemente ímpar. Caso contráriio, retorna False
    """

    bolArray = map(lambda x: x % 2, jogo)
    if len(jogo) % 2 != 0:
        return True if sum(bolArray) > np.floor(len(jogo) / 2) else False
    else:
        return True if sum(bolArray) > (len(jogo) / 2) else False


def gap(jogo):
    """Checa os espaçamentos entre números consecutivos(extremos inclusive)

    :return: Array com os espaçamentos
    """
    gaps = []
    for i in range(0, len(jogo) - 1):
        gaps.append(jogo[i + 1] - jogo[i])
    return gaps


def sequences(jogo):
    """Checa as sequências ininterruptas presentes

    :return: Quantia de números em cada sequência
    """
    gaps = gap(jogo)
    s = 1
    seq = []
    for i in range(0, len(gaps)):
        if gaps[i] == 1:
            s += 1
        else:
            seq.append(s)
            s = 1
    else:
        seq.append(s)
    return seq


def nPrimeNumbers(jogo):
    """Checa a quantia de números primos presentes no jogo

    :param jogo: Jogo a ser analisado
    :return: Número de primos presente
    """
    primeNumbers = []
    for i in jogo:
        s = 0
        for j in range(1, int(i) + 1):
            if i % j == 0:
                s += 1
        if s == 2:
            primeNumbers.append(i)
    return np.intersect1d(primeNumbers, jogo).size


if __name__ == "__main__":
    populate_games()
