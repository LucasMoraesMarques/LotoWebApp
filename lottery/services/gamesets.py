from typing import List
from django.contrib.auth import get_user_model
from django.db.models import F
import io
import pandas as pd
from LotoWebApp import settings
from lottery.services import email_sending


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
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    wbook = writer.book
    for games_set in games_sets:
        numbers_list = [[f"Jogo {index+1}"] + game.arrayNumbers for index, game in enumerate(games_set.games.all())]
        df_columns = ["Jogo"] + [f"Bola {i}" for i in range(1, games_set.gameLength +1)]
        df = pd.DataFrame(numbers_list, columns=df_columns)
        df.rename(columns={"arrayNumbers": "Números"}, inplace=True)
        df.to_excel(writer, index=False, sheet_name=f"{games_set.name}")
        wsheet = writer.sheets[f"{games_set.name}"]
        wsheet.set_default_row(20)
        formats = wbook.add_format({"align": "center"})
        formats.set_align("vcenter")
        for column in df.columns:
            column_width = max(df[column].astype(str).map(len).max() + 2, len(column) + 2)
            col_idx = df.columns.get_loc(column)
            formatting = formats
            wsheet.set_column(col_idx, col_idx, column_width, formatting)
    wbook.close()
    output.seek(0)
    return {"content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "output": output,
            "file_name": "conjuntos-de-jogos-selecionados.xlsx"}


def export_games_sets_by_csv(games_sets):
    output = io.StringIO()
    data = pd.DataFrame()
    for games_set in games_sets:
        numbers_list = [[f"Jogo {index + 1}"] + game.arrayNumbers for index, game in enumerate(games_set.games.all())]
        df_columns = ["Jogo"] + [f"Bola {i}" for i in range(1, games_set.gameLength + 1)]
        df = pd.DataFrame(numbers_list,
                          columns=df_columns)
        df.rename(columns={"arrayNumbers": "Números"}, inplace=True)
        data = pd.concat([data, df], axis=0)
    data.to_csv(output, index=False)
    output.seek(0)
    return {"content_type": "text/csv", "output": output,
            "file_name": "conjuntos-de-jogos-selecionados.csv"}


def send_by_email(user, games_sets):
    emails_info = {"SUBJECT": "Conjuntos de Jogos | LotoAssistant",
                   "BODY": "Seguem os conjuntos de jogos selecionados.", "FROM": settings.DEFAULT_FROM_EMAIL,
                   "TO": [user.email], "TEMPLATE": "emails/template1.html",
                   "FILE": export_games_sets_by_excel(games_sets), "USER": user}
    email_sending.send_games_sets_by_email(emails_info)


def send_by_whatsapp(user, results, user_results):
    from twilio.rest import Client

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    message = client.messages.create(
        from_='whatsapp:+14155238886',
        body=f'Oĺá, {user.first_name} {user.last_name}. Segue os arquivos de resultados selecionados.',
        to='whatsapp:+553183086959',
    )
    for result_id in results:
        result = user_results.filter(id=result_id).first()
        if result:
            message = client.messages.create(
                from_='whatsapp:+14155238886',
                to='whatsapp:+553183086959',
                media_url=result.report_file.url
            )
