import numpy as np
import pandas as pd
from lottery.models import Lottery, Game
import random


def simple(lototype, nPlayed, nJogos, removedNumbers, fixedNumbers):
    """ Gerador simples. Sem filtros específicos

    :param nPlayed: Quantidade de números escolhidos por jogo
    :param nJogos: Número de jogos a ser criado
    :param removedNumbers: Números removidos
    :param fixedNumbers: Números fixados
    :return: None. Cria n jogos pedidos pelo user
    """
    loto = Lottery.objects.get(name=lototype)
    nFixed = len(fixedNumbers)
    nPossibles = range(1, loto.numbersRangeLimit+1)
    print(loto.possiblesChoicesRange)
    jogos = [0]
    numbersAllowed = np.array(np.setdiff1d(np.array(nPossibles), removedNumbers))
    numbersAllowed = np.setdiff1d(numbersAllowed, fixedNumbers)

    cont = 0
    while cont < nJogos:
        numbersAllowedCopy = list(numbersAllowed)
        random.shuffle(numbersAllowedCopy)
        np.random.RandomState(cont)
        jogo = np.zeros(nPlayed - nFixed)
        for i in range(0, jogo.size):
            number = np.random.choice(numbersAllowedCopy, 1)
            jogo[i] = number
            numbersAllowedCopy.remove(number)

        jogo = np.union1d(jogo, fixedNumbers).astype("int8")
        jogo = list(jogo)
        if jogo in jogos:
            continue
        else:
            jogos.append(jogo)
            cont += 1

    jogos.pop(0)
    jogos = pd.DataFrame(jogos)
    return jogos


def smart(lototype, nJogos, removedNumbers, fixedNumbers, kwargs):
    """ Gerador inteligente que realiza queries na database de combinações possíveis

    :param nPlayed: Quantidade de números escolhidos por jogo
    :param removedNumbers: Números removidos
    :param fixedNumbers: Números fixados
    :param kwargs: Filtros específicos para a query
    :return: None. Cria n jogos pedidos pelo user dentro dos possíveis
    """
    games = calc_combs(lototype, removedNumbers, fixedNumbers, kwargs)
    games = pd.DataFrame(games.values())
    index = list(games.index)
    random.shuffle(index)
    games = games.iloc[index, :]
    games = games[:nJogos]
    return games


def calc_combs(lototype, numbersRemoved, numbersFixed, kwargs):
    """ Calcula todas as combinações com os filtro dados através da database de todos os jogos

    :param lototype: Loteria escolhida
    :param numbersRemoved: Números removidos
    :param numbersFixed: Números fixados
    :param kwargs: Filtros inteligentes
    :return: Todas as combinações válidas
    """
    loto = Lottery.objects.get(name=lototype)
    games = Game.objects.filter(lottery=loto)
    for removed in numbersRemoved:
        games = games.exclude(arrayNumbers__contains=[removed])
    for fixed in numbersFixed:
        games = games.filter(arrayNumbers__contains=[fixed])
    print(games.count())
    print(kwargs)
    for k, v in kwargs.items():
        if k == "nPrimes":
            games = games.filter(n_primes=v)
        elif k == "maxSeq":
            games = games.filter(max_seq__lte=v)
        elif k == "minSeq":
            games = games.filter(min_seq__gte=v)
        elif k == "maxGap":
            games = games.filter(max_gap__lte=v)
        elif k == "isOdd":
            games = games.filter(is_odd=v)
    return games

