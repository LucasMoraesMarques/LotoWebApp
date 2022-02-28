from typing import List
from django.contrib.auth import get_user_model
from django.db.models import F


def all(user):
    return user.gamesets.all().order_by('-createdAt')


def historic(user, n=5):
    return all(user)[:n]


def apply_action(games_sets_ids: List[int], games_ids: List[int], action: str, user: get_user_model) -> str:
    user_games_sets = all(user)
    games_sets_to_update = user_games_sets.filter(id__in=games_sets_ids)
    print(action)
    if action == "ATIVAR":
        action_name = "ATIVADOS"
        games_sets_to_update.update(isActive=True)
    elif action == "DESATIVAR":
        action_name = "DESATIVADOS"
        games_sets_to_update.update(isActive=False)
    elif action == "DELETAR":
        action_name = "DELETADOS"
        games_sets_to_update.delete()
    elif action == "REMOVER":
        action_name = "REMOVIDOS"
        remove_games(games_sets_to_update[0], games_ids)
    return action_name


def update_quantifiers(instance, games_ids, collections_list, game_length):
    instance.games.set(games_ids)
    instance.numberOfGames = len(games_ids)
    instance.gameLength = game_length
    instance.collections.set(collections_list)
    instance.save()


def remove_games(games_set, games_ids):
    for game_id in games_ids:
        games_set.games.remove(int(game_id))
    games_set.numberOfGames -= len(games_ids)
    games_set.save()


def check_in_collection(games_sets, collection):
    games_sets = games_sets.prefetch_related("collections").annotate(include=F("isActive"))
    for games_set in games_sets:
        if collection in games_set.collections.all():
            games_set.include = True
        else:
            games_set.include = False
    return games_sets
