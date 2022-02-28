import numpy as np
import pandas as pd
from lottery.models import Game, Draw, GameParity
from typing import List, Dict

def parity(jogo):
    bol_array = map(lambda x: x % 2, jogo)
    if len(jogo) % 2 != 0:
        if sum(bol_array) > np.floor(len(jogo) / 2):
            return GameParity.ODD
        else:
            return GameParity.EVEN
    else:
        if sum(bol_array) == len(jogo) / 2:
            return GameParity.NEUTRAL
        elif sum(bol_array) > len(jogo) / 2:
            return GameParity.ODD
        else:
            return GameParity.EVEN


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


def numbers_ranking(data, lottery):
    """Rankeia os números mais sorteados na database de resultados

    :return: Ranking
    """
    df = pd.DataFrame(data)
    data_list = []
    for index, row in df.iterrows():
        data_list.append(row[0])
    df = pd.DataFrame(data_list)
    rank = dict()
    for i in range(1, lottery.numbersRangeLimit + 1):
        v = np.where(df == i, True, False).sum()
        rank[i] = v
    rank_series = pd.Series(rank)
    rank_series.sort_values(ascending=False, inplace=True)
    rank_series.name = "Ranking Geral"
    return rank_series


def numbers_metadata(qs):
    metadata = {
        "n_primes": {},
        "max_seq": {},
        "min_seq": {},
        "max_gap": {},
        "parity": {},
        "sum": {}
    }
    properties = ["n_primes", "parity", "sum", "max_seq", "min_seq", "max_gap"]
    for entry in qs:
        for prop in properties:
            value = eval(f"entry.{prop}", {"entry": entry})
            if value in metadata[prop].keys():
                metadata[prop][value] += 1
            else:
                metadata[prop][value] = 1
    return metadata


def parity_balance(numbers: List[int]) -> Dict[str, int]:
    balance = {
        "odd": 0,
        "even": 0
    }
    for number in numbers:
        if number % 2 == 0:
            balance["even"] += 1
        else:
            balance["odd"] += 1
    return balance


def latest_frequency_in_draws(numbers, draws):
    frequency = {
        number: 0 for number in numbers
    }
    for number in numbers:
        for draw in draws:
            if number in draw.result:
                frequency[number] += 1
            else:
                break
    return frequency
