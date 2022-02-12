import numpy as np
import pandas as pd
from lottery.models import Draw


def numbers_ranking(draws):
    """Rankeia os números mais sorteados na database de resultados

    :return: Ranking
    """
    lottery = draws[0].lottery
    draws = pd.DataFrame(draws.values_list("result"))
    draws_list = []
    for index, row in draws.iterrows():
        draws_list.append(row[0])
    draws = pd.DataFrame(draws_list)
    rank = dict()
    for i in range(1, lottery.numbersRangeLimit + 1):
        v = np.where(draws == i, True, False).sum()
        rank[f'{i}'] = v
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
