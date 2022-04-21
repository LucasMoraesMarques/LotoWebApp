import os.path

from babel.dates import format_date
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from lottery.models import Result
from LotoWebApp import settings
from io import BytesIO


def create_text_report_file(draw, total_scores, collection, total_balance, abridged=False):
    result = draw.result
    lottery = draw.lottery
    scores_interval = draw.lottery.possiblesPointsToEarn
    scores_by_games_set = total_scores["Conjuntos"]
    total_by_scores = total_scores["Total"]
    balance_labels = ['Premiacao', 'Valor Gasto', 'Saldo']
    file_name = f'{collection.name.replace(" ", "_")}_{draw.number}_{"resumido" if abridged else "completo"}.txt'
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
            for game_number, score in scores["Jogos"].items():
                lines.append(f"\nJogo {game_number}: {score} acertos")

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
    file_path = os.path.join(f"resultados/usuario_{collection.user.id}/{lottery.name}/{draw.number}/txt/{file_name}")
    if default_storage.exists(file_path):
        output = default_storage.open(file_path, "w+")
        output.write("".join(lines))
        output.close()
    else:
        default_storage.save(file_path, ContentFile("".join(lines)))

    result_obj, was_created = Result.objects.get_or_create(
        lottery=lottery,
        collection=collection,
        draw=draw,
        number_of_game_sets=len(scores_by_games_set),
        number_of_games=total_balance["Total Geral"]["Numero de Jogos"],
        report_file=file_path,
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
