from typing import List
from django.contrib.auth import get_user_model
from django.db.models import F
import io
from lottery.models import Games, Gameset
from LotoWebApp import settings
from lottery.services import email_sending
import pandas as pd


def all(user):
    return user.gamesets.all().order_by('-createdAt')


def historic(user, n=5):
    return all(user)[:n]


def apply_action(games_sets_ids: List[int], games_ids: List[int], action: str, user: get_user_model) -> str:
    user_games_sets = all(user)
    games_sets_to_update = user_games_sets.filter(id__in=games_sets_ids)
    print(action)
    action = action.upper()
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


def export_games_sets_by_excel(games_sets):
    output = io.BytesIO()
    data = games.values("lottery__name", "arrayNumbers")
    df = pd.DataFrame(data)
    df.rename(columns={"lottery__name": "Loteria",
                       "arrayNumbers": "Números",
                       }, inplace=True)
    game_length = len(df["Números"][0])
    df = pd.concat([df, pd.DataFrame(df["Números"].tolist(), columns=[f"Bola {i}" for i in range(1, game_length + 1)])],
                   axis=1)
    df.drop("Números", inplace=True, axis=1)
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, index=False, sheet_name=f"Jogos")
    wbook = writer.book
    wsheet = writer.sheets[f"Jogos"]
    wsheet.set_default_row(30)
    formats = wbook.add_format({"align": "center"})
    formats.set_align("vcenter")
    for column in df.columns:
        column_width = max(df[column].astype(str).map(len).max() + 10, len(column) + 5)
        col_idx = df.columns.get_loc(column)
        formatting = formats
        wsheet.set_column(col_idx, col_idx, column_width, formatting)
    wbook.close()
    output.seek(0)
    return {"content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "output": output,
            "file_name": "jogos-selecionados.xlsx"}


def export_games_sets_by_csv(games):
    output = io.StringIO()
    data = games.values("lottery__name", "arrayNumbers")
    df = pd.DataFrame(data)
    df.rename(columns={"lottery__name": "Loteria",
                       "arrayNumbers": "Números",
                       }, inplace=True)
    game_length = len(df["Números"][0])
    df = pd.concat([df, pd.DataFrame(df["Números"].tolist(), columns=[f"Bola {i}" for i in range(1, game_length + 1)])], axis=1)
    df.drop("Números", inplace=True, axis=1)
    df.to_csv(output)
    output.seek(0)
    return {"content_type": "text/csv", "output": output,
            "file_name": "jogos-selecionados.csv"}
