import numpy as np
from lottery.models import Game, Draw, GameParity


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
