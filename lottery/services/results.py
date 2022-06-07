import io
import os.path

from babel.dates import format_date
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from lottery.models import Result
from LotoWebApp import settings
from lottery.services import email_sending
from io import BytesIO
import pandas as pd
import requests
import csv
from fpdf import FPDF


def create_text_report_file(draw, total_scores, collection, total_balance, abridged=False):
    result = draw.result
    lottery = draw.lottery
    scores_interval = draw.lottery.possiblesPointsToEarn
    scores_by_games_set = total_scores["Conjuntos"]
    total_by_scores = total_scores["Total"]
    balance_labels = ['Premiacao', 'Valor Gasto', 'Saldo']
    file_name = f'{collection.name.replace(" ", "_")}_{draw.number}_{"resumido" if abridged else "completo"}.pdf'
    lines = []
    result_text = ''
    for number in result:
        result_text += f"{number} - "
    result_text = result_text[:-2]
    lines.append(f"Resultado da Colecao {collection.name}".center(30, "="))
    lines.append(f"\n\nLoteria: {lottery.name} \n")
    lines.append(f"Concurso: {draw.number} \n")
    lines.append(f"Data: {format_date(draw.date, 'dd/MM/yyyy', 'pt_br')} \n")
    lines.append(f"Numeros: {result_text} \n")
    lines.append(f"Acumulou: {'Sim' if draw.hasAccumulated else 'Nao'}\n")
    if draw.hasAccumulated:
        lines.append(f"Premio estimado proximo concurso: R$ {draw.nextDrawEstimatedPrize: ,.2f}\n")
    else:
        lines.append(f"Premio {scores_interval[-1]} acertos: R$ {draw.maxPrize:,.2f}")
    for games_set_name, scores in scores_by_games_set.items():
        lines.append(f"\n\n{games_set_name:=^30}\n")
        lines.append(f"\n\nBalanco de Acertos\n")
        for score in total_by_scores.keys():
            lines.append(f"\n{score}: {scores['Total'][score]}")
        lines.append(f"\n\nBalanco Monetario\n")
        for label in balance_labels:
            lines.append(f"\n{label}: R$ {total_balance['Por conjunto'][games_set_name][label]:,.2f}")
        lines.append('\n')
        if not abridged:
            lines.append(f"\n\nBalanco por Jogo\n")
            for game_number, score in enumerate(scores["Jogos"].values()):
                lines.append(f"\nJogo {game_number + 1}: {score} acertos")

    if len(scores_by_games_set) > 1:
        lines.append(f"\n\n{'':=^30}")
        lines.append(f"\n\nBalanco de Acertos Geral\n")
        for label, score in total_by_scores.items():
            lines.append(f"\n{label}: {score}")
        lines.append(f"\n\nBalanco Monetario Geral\n")
        for label in balance_labels:
            lines.append(f"\n{label}: R$ {total_balance['Total Geral'][label]:,.2f}")
        lines.append(f"\nNumero de Jogos: {total_balance['Total Geral']['Numero de Jogos']:,.2f}")
        lines.append('\n')
    file_path = f"resultados/usuario_{collection.user.id}/{lottery.name}/{draw.number}/{file_name}"

    if default_storage.exists(os.path.join(settings.MEDIA_ROOT, file_path)):
        output = default_storage.open(file_path, "w+")
        output.write("".join(lines))
        output.close()
    else:
        """ Save string io buffer in S3
        output = io.StringIO()
        output.writelines(lines)
        output.seek(0)
        default_storage.save(file_path, ContentFile(output.getvalue().encode("utf-8")))"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.multi_cell(0, 10, "".join(lines))
        content = (bytes(pdf.output(file_path, dest='S'), encoding='latin1'))
        default_storage.save(os.path.join(settings.MEDIA_ROOT, file_path), ContentFile(content))

    result_obj, was_created = Result.objects.get_or_create(
        lottery=lottery,
        collection=collection,
        draw=draw,
        number_of_game_sets=len(scores_by_games_set),
        number_of_games=total_balance["Total Geral"]["Numero de Jogos"],
        report_file=os.path.join(settings.MEDIA_ROOT, file_path),
        abridged=abridged)
    if was_created:
        result_obj.points_info = total_scores
        result_obj.money_balance = total_balance
        result_obj.save()
    return result_obj.report_file.url, result_obj


def check_scores_in_draw(draw, games_sets):
    scores_interval = draw.lottery.possiblesPointsToEarn
    scores_by_games_set = {
        "Total": {f'{i} acertos': 0 for i in scores_interval},
        "Conjuntos": {}
    }
    for games_set in games_sets:
        scores_by_games_set["Conjuntos"][games_set.name] = {}
        scores_by_games_set["Conjuntos"][games_set.name]["Total"] = {
            f'{i} acertos': 0 for i in scores_interval
        }
        scores_by_games_set["Conjuntos"][games_set.name]["Jogos"] = {}
        scores_by_games_set["Conjuntos"][games_set.name]["gameLength"] = games_set.gameLength
        for game in games_set.games.all():
            score = len(set(game.arrayNumbers) & set(draw.result))
            scores_by_games_set["Conjuntos"][games_set.name]["Jogos"][f"{game.id}"] = score
            if score in scores_interval:
                scores_by_games_set["Conjuntos"][games_set.name]["Total"][f'{score} acertos'] += 1
                scores_by_games_set["Total"][f'{score} acertos'] += 1
    return scores_by_games_set


def check_prizes_in_draw(draw, total_scores):
    lottery = draw.lottery
    scores_interval = lottery.possiblesPointsToEarn
    prices_ranges = lottery.possiblesPricesRange
    default_choices_number = lottery.possiblesChoicesRange[0]
    scores_by_games_set = total_scores["Conjuntos"]
    total_balance = {
        "Por conjunto": {},
        "Total Geral":
            {'Premiacao': 0,
             'Valor Gasto': 0,
             'Saldo': 0,
             'Numero de Jogos': 0}
    }
    total_by_games_sets = {
        key: {
            'Premiacao': 0,
            'Valor Gasto': 0,
            'Saldo': 0,
            'Numero de Jogos': 0
        } for key in scores_by_games_set.keys()
    }
    for games_set_name, games_set_scores in scores_by_games_set.items():
        total_games = len(games_set_scores["Jogos"])
        total_scores = games_set_scores["Total"]
        games_length = games_set_scores["gameLength"]
        total_by_games_sets[games_set_name]['Premiacao'] = 0
        total_by_games_sets[games_set_name]['Valor Gasto'] = total_games * prices_ranges[
            games_length - default_choices_number]
        total_by_games_sets[games_set_name]['Numero de Jogos'] = total_games
        for score in scores_interval:
            for prizes_range, prizes_info in draw.metadata[0].items():
                if int(prizes_info['descricaoFaixa'].split(" ")[0]) == score:
                    total_by_games_sets[games_set_name]['Premiacao'] += (
                                total_scores[f'{score} acertos'] * prizes_info['valorPremio'])
        total_by_games_sets[games_set_name]['Saldo'] = total_by_games_sets[games_set_name]['Premiacao'] - \
                                                       total_by_games_sets[games_set_name]['Valor Gasto']
        balance_labels = ['Premiacao', 'Valor Gasto', 'Saldo']
        for label in balance_labels:
            total_balance["Total Geral"][label] += total_by_games_sets[games_set_name][label]
        total_balance["Total Geral"]['Numero de Jogos'] += total_by_games_sets[games_set_name]['Numero de Jogos']
    total_balance["Por conjunto"] = total_by_games_sets
    return total_balance


def get_by_user(user):
    results = Result.objects.all()
    results = results.select_related("collection", "collection__user", "lottery", "draw")
    results = results.filter(collection__user=user)
    return results


def parse_money_balance_json(money_balance):
    parsed_dict = {
        "total": {
            "balance": money_balance["Total Geral"]["Saldo"],
            "cost": money_balance["Total Geral"]["Valor Gasto"],
            "prize": money_balance["Total Geral"]["Premiacao"]
        }
    }
    return parsed_dict


def parse_points_by_games_sets_json(result, points_by_games_sets):
    result_collection = result.collection
    results_games_sets = result_collection.gamesets.filter(name__in=points_by_games_sets.keys())
    points_by_games_sets_and_games = {}
    for games_set in results_games_sets:
        games_set_games = games_set.games.all()
        points_by_games = points_by_games_sets[games_set.name]["Jogos"]
        points_by_games_sets_and_games[games_set.name] = {}
        for game in games_set_games:
            points_by_games_sets_and_games[games_set.name][game.id] = {
                "numbers": game.arrayNumbers,
                "points": points_by_games.get(str(game.id), '-')
            }
    return points_by_games_sets_and_games


def historic(user_results, collection):
    results = user_results.filter(collection=collection).order_by("draw__number")
    historic_balance = {}
    for result in results:
        historic_balance[result.id] = {
            "balance": parse_money_balance_json(result.money_balance),
            "draw": result.draw
        }
    return historic_balance


def send_by_email(user, results, user_results):
    emails_info = {
        f"{user.username}": [{"SUBJECT": "Resultados dos Jogos | LotoAssistant",
                              "BODY": "Seguem os resultados dos seus jogos.",
                              "FROM": settings.DEFAULT_FROM_EMAIL,
                              "TO": [user.email],
                              "TEMPLATE": "emails/template1.html",
                              "FILES": []}],

    }
    for result_id in results:
        result = user_results.filter(id=result_id).first()
        if result:
            emails_info[f"{user.username}"][0]["FILES"].append(result.report_file)
    email_sending.custom_send_email(emails_info)


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


def parse_data_to_export(df):
    df["points_info"] = df["points_info"].apply(lambda x: x["Total"])
    df["money_balance"] = df["money_balance"].apply(lambda x: x["Total Geral"])
    money_balance_keys = df.loc[0, "money_balance"].keys()
    points_keys = df.loc[0, "points_info"].keys()
    for key in points_keys:
        df[key] = 0
    for key in points_keys:
        df[key] = df["points_info"].apply(lambda x: x[key])

    for key in money_balance_keys:
        df[key] = 0
    for key in money_balance_keys:
        df[key] = df["money_balance"].apply(lambda x: x[key])
    df.drop(["points_info", "money_balance", "Numero de Jogos"], axis=1, inplace=True)
    df.rename(columns={"number_of_game_sets": "Nº de Conjuntos",
                       "number_of_games": "Nº de Jogos",
                       "collection__name": "Coleção",
                       "draw__number": "Concurso",
                       "lottery__name": "Loteria",
                       "Premiacao": "Premiação",
                       }, inplace=True)
    df = df[["Coleção", "Loteria", "Concurso", "Nº de Conjuntos", "Nº de Jogos", "Valor Gasto", "Premiação", "Saldo",
             *points_keys]]
    return df


def export_by_excel(results):
    output = io.BytesIO()
    data = results.values("number_of_game_sets", "number_of_games", "points_info", "money_balance", "collection__name", "draw__number", "lottery__name")
    df = pd.DataFrame(data)
    df = parse_data_to_export(df)
    writer = pd.ExcelWriter(output, engine="xlsxwriter")
    df.to_excel(writer, index=False, sheet_name=f"Resultados")
    wbook = writer.book
    wsheet = writer.sheets[f"Resultados"]
    wsheet.set_default_row(30)
    formats = wbook.add_format({"align": "center"})
    formats.set_align("vcenter")
    money_format = wbook.add_format({"num_format": "R$ #,##0.00", "align": "center"})
    money_format.set_align("vcenter")
    for column in df.columns:
        column_width = max(df[column].astype(str).map(len).max() + 10, len(column) + 5)
        col_idx = df.columns.get_loc(column)
        formatting = formats
        if column in ["Valor Gasto", "Premiação", "Saldo"]:
            formatting = money_format
        wsheet.set_column(col_idx, col_idx, column_width, formatting)
    wbook.close()
    output.seek(0)
    return {"content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "output": output,
            "file_name": "resultados.xlsx"}


def export_by_csv(results):
    output = io.StringIO()
    data = results.values("number_of_game_sets", "number_of_games", "points_info", "money_balance", "collection__name",
                          "draw__number", "lottery__name")
    df = pd.DataFrame(data)
    df = parse_data_to_export(df)
    df.to_csv(output)
    output.seek(0)
    return {"content_type": "text/csv", "output": output,
            "file_name": "resultados.csv"}


def export_results_games_by_excel(games):
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


def export_results_games_by_csv(games):
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
