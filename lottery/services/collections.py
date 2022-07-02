from django.db.models import F, QuerySet
import io
import pandas as pd
from LotoWebApp import settings
from lottery.services import email_sending
from lottery.models import Gameset, Collection
import zipfile


def get_by_user(user):
    qs = user.collections.all().order_by('-createdAt')
    qs = qs.annotate(loto_name=F("lottery__name"))
    return qs


def historic(user, n=5):
    return get_by_user(user)[:n]


def apply_action(collections_to_update: QuerySet[Collection], games_sets_ids, user_games_sets, action: str) -> str:
    action = action.upper()
    message = ""
    if action == "ATIVAR":
        collections_to_update.update(is_reported=True)
        message = "Coleções ATIVADAS com sucesso!"
    elif action == "DESATIVAR":
        collections_to_update.update(is_reported=False)
        message = "Coleções DESATIVADAS com sucesso!"
    elif action == "DELETAR":
        action_name = "DELETADOS"
        #collections_to_update.delete()
        message = "Coleções DELETADAS com sucesso!"
    elif action == "ADICIONAR":
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
        message = "Conjuntos ADICIONADOS com sucesso!"
    return message


def update_quantifiers(instances, games_ids):
    for instance in instances:
        instance.numberOfGames += len(games_ids)
        instance.numberOfGamesets += 1
        instance.save()


def export_collections_by_excel(collections):
    output_zip = io.BytesIO()
    outputs_files = []
    for collection in collections:
        output = io.BytesIO()
        writer = pd.ExcelWriter(output, engine="xlsxwriter")
        wbook = writer.book
        games_sets = collection.gamesets.all()
        if games_sets:
            for games_set in games_sets:
                numbers_list = [[f"Jogo {index + 1}"] + game.arrayNumbers for index, game in
                                enumerate(games_set.games.all())]
                df_columns = ["Jogo"] + [f"Bola {i}" for i in range(1, games_set.gameLength + 1)]
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
        outputs_files.append([f"{collection.name}.xlsx", output])
    with zipfile.ZipFile(output_zip, mode="w") as zip_file:
        for file_name, output_file in outputs_files:
            with output_file:
                zip_file.writestr(file_name, output_file.getvalue())
    output_zip.seek(0)
    return {"content_type": "application/octet-stream", "output": output_zip,
            "file_name": "colecoes-selecionadas.zip"}


def export_collections_by_csv(collections):
    output_zip = io.BytesIO()
    outputs_files = []
    for collection in collections:
        output = io.StringIO()
        data = pd.DataFrame()
        games_sets = collection.gamesets.all()
        if games_sets:
            for games_set in games_sets:
                numbers_list = [[f"Jogo {index + 1}"] + game.arrayNumbers for index, game in
                                enumerate(games_set.games.all())]
                df_columns = ["Jogo"] + [f"Bola {i}" for i in range(1, games_set.gameLength + 1)]
                df = pd.DataFrame(numbers_list, columns=df_columns)
                df.rename(columns={"arrayNumbers": "Números"}, inplace=True)
                data = pd.concat([data, df], axis=0)
            data.to_csv(output, index=False)
        output.seek(0)
        outputs_files.append([f"{collection.name}.csv", output])
    with zipfile.ZipFile(output_zip, mode="w") as zip_file:
        for file_name, output_file in outputs_files:
            with output_file:
                zip_file.writestr(file_name, output_file.getvalue())
    output_zip.seek(0)
    return {"content_type": "application/octet-stream", "output": output_zip,
            "file_name": "colecoes-selecionadas.zip"}


def send_by_email(user, collections):
    emails_info = {"SUBJECT": "Coleções de Conjuntos | LotoAssistant",
                   "BODY": "Seguem as coleções de conjuntos de jogos selecionadas.", "FROM": settings.DEFAULT_FROM_EMAIL,
                   "TO": [user.email], "TEMPLATE": "emails/template1.html",
                   "FILE": export_collections_by_excel(collections), "USER": user}
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

