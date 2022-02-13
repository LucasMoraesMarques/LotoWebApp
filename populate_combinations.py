import os
import django
import pandas as pd
import re
from math import comb
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LotoWebApp.settings")
django.setup()
from lottery.models import Draw, Lottery, Combinations
from django.db.models import F
LOTTERY_CHOICES = {"lotofacil": 1, "diadesorte": 2, "megasena": 3}


def makeCombinations(n, nRange):
    """ Cria todas as combinações dos números de nRange tomados n a n.

    :param n: tamanho da n-upla
    :param nRange: intervalo para combinar (1 a nRange)
    :return: todas as Comb(nRange, n)

    Para cada n, cria-se uma sequência binária:
        n=2 -> 0b11 até 0b110000000 ... nRange-2 zeros
        n=3 -> 0b111 até 0b1110000000 ... nRange-3 zeros
    A regra do início é:
        n=2 -> 0b11 = 3 -> 2**2 - 1
        n=3 -> 0b111 = 7 -> 2**3 - 1
        n       ...         2**n - 1
    A regra do fim é:
        n=2, nRange = 5 -> 0b11000 = 2**nRange-1 + 2**nRange-2
        n, nRange   ...    0b1100000..0 = 2**nRange-1 + 2**nRange-2 +...+ 2**nRange-n
    """
    inicio = 2**n - 1
    fim = 0

    for i in range(1, n+1):
        fim += 2**(nRange-i)

    jogos = []
    for i in range(inicio, fim + 1):
        iCopy = format(i, 'b').zfill(nRange)
        if iCopy.count("1") == n:
            x = re.split(r"([01])", iCopy)
            x = [j for j in x if j not in [""]]
            jogos.append(x)
        else:
            continue

    return jogos


def makeCombinationsCartesian(n, nRange):
    combs = []
    logic = ""
    for i in range(1, n + 1):
        logic += "\t" * (i-1) + f"for number{i} in range(1, nRange + 1):\n"
    logic += "\t" * i + "new_comb = "
    numbers = "{"
    for j in range(1, n + 1):
        numbers += f"number{j}, "
    numbers += "}\n"
    logic += numbers
    logic += "\t" * i + "if len(new_comb) == n:\n"
    logic += "\t" * (i+1) + "new_comb = sorted(new_comb)\n"
    logic += "\t" * (i+1) + "if new_comb not in combs:\n"
    logic += "\t" * (i+3) + "combs.append(new_comb)\n"
    print(logic)
    exec(logic, {"nRange": nRange, "n": n, "combs":combs})
    print(combs)
    return combs



def binaryMapping(nUplas):
    """Decodifica as combinações binárias em jogos

    :param nUplas: n-uplas binárias geradas por makeCombinations
    :return: n-uplas mapeadas em jogos
    """
    combsMapped = []
    for comb in nUplas:
        a = []
        for i, j in enumerate(comb):
            if j == '1':
                a.append(i+1)
        combsMapped.append(set(a))
    return combsMapped


def checkCombinations(combs, jogos):
    """Rankeia as n-uplas em relação a database de resultados da loteria dada

    :param combs: Todas as n-uplas mapeadas em jogos
    :param jogos: Jogos da database de resultados
    :return: Series com o ranking das n-uplas
    """
    combs = [set(comb) for comb in combs]
    dictCombsRanking = {f"{comb}": 0 for comb in combs}

    for index, jogo in jogos.iterrows():
        for comb in combs:
            if comb.issubset(jogo):
                dictCombsRanking[f"{comb}"] += 1

    rankingSeries = pd.Series(dictCombsRanking)
    return rankingSeries.sort_values(ascending=False)


def get_draws(lottery):
    draws = Draw.objects.filter(lottery=lottery)
    return draws


def create_combs(draws, lottery, n):
    nTotal = comb(lottery.numbersRangeLimit, n)
    print(f"O número de combinações de {lottery.numbersRangeLimit} tomadas {n} a {n} é {nTotal}")
    print("\nEsse processo pode demorar muito dependendo do total de combinações")
    print(f"\nCalculando ...")
    combs = makeCombinationsCartesian(n, lottery.numbersRangeLimit)
    ranking = checkCombinations(combs, draws)
    for numbers, repetitions in ranking.items():
        Combinations.objects.create(
            lottery=lottery,
            n=n,
            numbers=numbers,
            repetitions=repetitions
        )


def update_combs(draws, lottery):
    combinations = Combinations.objects.filter(lottery=lottery)
    combinations.update(repetitions=0)
    for draw in draws:
        filtered_combs = combinations.filter(numbers__contained_by=draw.result)
        filtered_combs.update(repetitions=F("repetitions") + 1)


def main():
    lottery = Lottery.objects.get(id=3)
    draws = get_draws(lottery)
    update_combs(draws, lottery)
    print(len(draws))
    """
    n = 2
    draws = pd.DataFrame(draws.values_list("result"))
    draws_list = []
    for index, row in draws.iterrows():
        draws_list.append(row[0])
    draws = pd.DataFrame(draws_list)
    create_combs(draws, lottery, n)"""

main()