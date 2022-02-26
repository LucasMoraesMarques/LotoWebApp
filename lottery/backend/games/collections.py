from django.db.models import F
from typing import List
from django.contrib.auth import get_user_model


def all(user):
    qs = user.collections.all().order_by('-createdAt')
    qs = qs.annotate(loto_name=F("lottery__name"))
    return qs


def historic(user, n=5):
    return all(user)[:n]


def apply_action(collections_ids: List[int], games_sets_ids, user_games_sets, action: str, user: get_user_model) -> str:
    user_collections = all(user)
    collections_to_update = user_collections.filter(id__in=collections_ids)
    if action == "ATIVAR":
        action_name = "ATIVADOS"
        collections_to_update.update(isActive=True)
    elif action == "DESATIVAR":
        action_name = "DESATIVADOS"
        collections_to_update.update(isActive=False)
    elif action == "DELETAR":
        action_name = "DELETADOS"
        collections_to_update.delete()
    elif action == "ADICIONAR":
        action_name = "ADICIONADOS"
        collection = collections_to_update[0]
        collection.numberOfGamesets = 0
        collection.numberOfGames = 0
        for games_set in user_games_sets:
            if games_set.id in games_sets_ids:
                collection.gamesets.add(games_set.id)
                collection.numberOfGamesets += 1
                collection.numberOfGames += games_set.numberOfGames
            else:
                collection.gamesets.remove(games_set.id)
            collection.save()
    return action_name


def update_quantifiers(instances, games_ids):
    for instance in instances:
        instance.numberOfGames += len(games_ids)
        instance.numberOfGamesets += 1
        instance.save()



