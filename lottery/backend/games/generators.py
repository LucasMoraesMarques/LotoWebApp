import math

import numpy as np
import pandas as pd
from lottery.models import Lottery, Game
import random
from typing import List, Dict, Any, Tuple, Iterable
from django.db.models import QuerySet
from django.http import QueryDict
from pandas.core.frame import DataFrame
FILTER_KEYS = ["nPrimes", "maxSeq", "minSeq", "maxGap", "isOdd"]


def simple(lottery: Lottery, game_length: int, number_of_games: int, removed_numbers: List[int], fixed_numbers: List[int]) -> DataFrame:
    number_of_fixed = len(fixed_numbers)
    numbers_range = range(1, lottery.numbersRangeLimit+1)
    games_list = [0]
    allowed_numbers = np.array(np.setdiff1d(np.array(numbers_range), removed_numbers))
    allowed_numbers = np.setdiff1d(allowed_numbers, fixed_numbers)
    cont = 0
    while cont < number_of_games:
        allowed_numbers_copy = list(allowed_numbers)
        random.shuffle(allowed_numbers_copy)
        np.random.RandomState(cont)
        game = np.zeros(game_length - number_of_fixed)
        for i in range(0, game.size):
            number = np.random.choice(allowed_numbers_copy, 1)
            game[i] = number
            allowed_numbers_copy.remove(number)

        game = np.union1d(game, fixed_numbers).astype("int8")
        game = list(game)
        if game in games_list:
            continue
        else:
            games_list.append(game)
            cont += 1

    games_list.pop(0)
    games = pd.DataFrame(games_list)
    return games


def smart(lottery: Lottery, number_of_games: int, removed_numbers: List[int], fixed_numbers: List[int], kwargs: Dict[Any, Any]) -> Tuple[DataFrame, List[int]]:
    games = get_games_from_db(lottery, removed_numbers, fixed_numbers, kwargs)
    games = pd.DataFrame(games.values())
    indexes = list(games.index)
    random.shuffle(indexes)
    indexes = indexes[:number_of_games]
    games = games.iloc[indexes, :]
    games_ids = []
    games_list = []
    for index, game in games.iterrows():
        games_list.append(game["arrayNumbers"])
        games_ids.append(game["id"])
    games = pd.DataFrame(games_list)
    return games, games_ids


def get_games_from_db(lottery: Lottery, removed_numbers: List[int], fixed_numbers: List[int], kwargs: Dict[Any, Any]) -> QuerySet[Game]:
    games = Game.objects.filter(lottery_id=lottery.id)
    game_length = lottery.possiblesChoicesRange[0]
    if len(removed_numbers) > game_length:
        for removed in removed_numbers:
            games = games.exclude(arrayNumbers__contains=[removed])
    else:
        games = games.exclude(arrayNumbers__contains=removed_numbers)
    games = games.filter(arrayNumbers__contains=fixed_numbers)
    for key, value in kwargs.items():
        if key == "nPrimes":
            games = games.filter(n_primes=value)
        elif key == "maxSeq":
            games = games.filter(max_seq__lte=value)
        elif key == "minSeq":
            games = games.filter(min_seq__gte=value)
        elif key == "maxGap":
            games = games.filter(max_gap__lte=value)
        elif key == "parity":
            games = games.filter(parity=value)
    return games


def parse_kwargs_filters(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    filters = {}
    for key in FILTER_KEYS:
        try:
            filter_value = kwargs.get(key)[0]
        except (KeyError, TypeError, IndexError):
            pass
        else:
            if filter_value:
                filters[key] = filter_value
    return filters


def parse_fixed_removed(data: QueryDict) -> Tuple[List[int], List[int]]:
    removed_numbers = [int(i) for i in data.getlist('nRemoved', [])]
    fixed_numbers = [int(i) for i in data.getlist('nFixed', [])]
    return removed_numbers, fixed_numbers


def calc_combs(lottery: Lottery, removed_numbers: List[int], fixed_numbers: List[int], filters: Dict[str, Any]) -> int:
    games = get_games_from_db(lottery, removed_numbers, fixed_numbers, filters)
    return games.count()


def get_or_create_by_dataframe(games: pd.DataFrame, lottery: Lottery) -> List[int]:
    games_ids = []
    for index, game in games.iterrows():
        game_list = game.to_list()
        game_list.sort()
        (game_obj, was_created) = Game.objects.get_or_create(arrayNumbers=game_list, lottery=lottery)
        games_ids.append(game_obj.id)
    return games_ids


def reverse_mapping(jogo, loto):
    lottery = Lottery.objects.get(name=loto)
    print(lottery.numbersRangeLimit)
    jogo0 = np.zeros(lottery.numbersRangeLimit)
    jogo = np.array(jogo)
    for number in jogo:
        jogo0[number-1] = 1
    number = 0
    for pos,value in enumerate(jogo0):
        number += value*math.pow(2,pos)
    return number