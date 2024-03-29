import io

from django.shortcuts import render, redirect
from lottery.forms import CreateCollectionForm, UploadCollectionForm
from lottery.models import Lottery, LOTTERY_CHOICES, Game, Draw, Gameset, Collection, Combinations
from django import forms
from django.http import JsonResponse
from django.db.models import Sum, F, Q, Case, When, Count
import pandas as pd
from lottery.services import generators, gamesets, collections, stats, results, email_sending
from lottery.forms import CustomUserCreationForm, LoginForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.http import HttpResponseRedirect, HttpResponse
from time import time
from django.forms.models import model_to_dict
from babel.dates import format_date
from django.shortcuts import get_object_or_404


@login_required
def create_collection(request):
    print(request.POST)
    if request.FILES:
        form = UploadCollectionForm(request.POST, request.FILES)
        if form.is_valid():
            data = {
                    'name': 'uploaded',
                    'id': 2,
                    'lottery': 'Megasena'
                }
            print(pd.read_csv(request.FILES['file'], delimiter=";"))
            return JsonResponse(data=data, status=200)
    else:
        form = CreateCollectionForm(request.POST)
        data = {}
        if form.is_valid():
            user_collections = collections.get_by_user(request.user)
            if user_collections.filter(name=form.cleaned_data["name"]).exists():
                data = {'error': "Já existe um coleção com esse nome. Tente novamente com outro nome!"}
            else:
                collection = form.save(request.user)
                data = {
                        'name': collection.name,
                        'id': collection.id,
                        'lottery': str(collection.lottery)
                    }
            return JsonResponse(data=data, status=200)
        return JsonResponse(data, status=400)


def landing(request):
    return render(request, "landing/pages/about-us.html")


@login_required
def dashboard(request):
    return render(request, "platform/dashboard/dashboard.html")


@login_required
def lotteries(request):
    lotteries_objs = Lottery.objects.all()
    draws = Draw.objects.all()
    draws = draws.annotate(lottery_name=F("lottery__name"))
    ordered_draws = draws.order_by('lottery_id', '-date')
    last_draws = ordered_draws.distinct('lottery_id')[:3]
    ctx = {
        'lotteries': lotteries_objs,
        'lastDraws': last_draws,
    }
    return render(request, "platform/dashboard/lotteries.html", ctx)


@login_required
def lottery_detail(request, name=''):
    draws = Draw.objects.all()
    draws = draws.annotate(lottery_name=F("lottery__name"))
    last_draws = draws.order_by('lottery_id', '-date').distinct('lottery_id')[:3]
    draws = draws.order_by('lottery_id', 'number').filter(lottery__name=name)
    lottery = draws[0].lottery
    ranking = stats.numbers_ranking(draws.values_list('result'), lottery)
    metadata = stats.numbers_metadata(draws)
    print(metadata)
    ctx = {
        'draws': draws,
        'lototypes': LOTTERY_CHOICES,
        'lastDraws': last_draws,
        "current": list(filter(lambda x: x[0] == name, LOTTERY_CHOICES))[0],
        "lottery": lottery,
        "ranking": ranking,
        "metadata": metadata,
    }
    return render(request, "platform/dashboard/lottery_detail.html", ctx)


@login_required
def games(request):
    lotteries_objs = Lottery.objects.all()
    user_games_sets = gamesets.get_by_user(request.user)
    last_games_sets = gamesets.historic(request.user)
    user_collections = collections.get_by_user(request.user)
    last_collections = collections.historic(request.user)
    collection_creation_form = CreateCollectionForm()
    upload_collection_file_form = UploadCollectionForm()
    if request.POST:
        form = forms.Form(request.POST)
        if form.is_valid():
            action = request.POST.get("action")
            games_sets_ids = [int(i) for i in request.POST.getlist("gamesets")]
            collections_ids = [int(i) for i in request.POST.getlist("collections")]
            print(request.POST)
            if games_sets_ids and action:
                action_name = gamesets.apply_action(games_sets_ids, [], action, request.user)
                messages.success(request, f"Conjuntos {action_name} com sucesso!")
            if collections_ids and action:
                action_name = collections.apply_action(collections_ids, [], [], action, request.user)
                messages.success(request, f"Coleções {action_name} com sucesso!")
            return redirect('lottery:games')
    games_sets_data = {
        'gamesets': user_games_sets,
        'lastGamesets': last_games_sets,
    }

    collections_data = {
        'collections': user_collections,
        'lastCollections': last_collections,
        'totalGamesets': user_games_sets.count(),
        'totalCollections': user_collections.count(),
        'totalGames': user_games_sets.aggregate(sum=Sum('numberOfGames'))
    }

    ctx = {
        'lotteries': lotteries_objs,
        'gamesetsData': games_sets_data,
        'collectionsData': collections_data,
        'collectionForm': collection_creation_form,
        'uploadCollectionForm': upload_collection_file_form,
    }
    return render(request, "platform/dashboard/games.html", ctx)


@login_required
def export_games_sets(request):
    user_games_sets = gamesets.get_by_user(request.user)
    games_sets_to_export = request.POST.getlist("games-sets", [])
    games_sets_to_export = user_games_sets.filter(id__in=games_sets_to_export).prefetch_related("games")
    if request.method == "POST":
        file_type = request.POST.get("file-type", "excel")
        handler = eval(f"gamesets.export_games_sets_by_{file_type}")
        data = handler(games_sets_to_export)

        response = HttpResponse(
            data["output"],
            content_type=data["content_type"],
        )
        response["Content-Disposition"] = f'attachment; filename={data["file_name"]}'
        return response


@login_required
def edit_games_sets(request):
    user_games_sets = gamesets.get_by_user(request.user)
    games_sets_to_edit = request.POST.getlist("games-sets", [])
    is_detail_view = request.POST.get("is_detail", "False")
    games_sets_to_edit = user_games_sets.filter(id__in=games_sets_to_edit).prefetch_related("games")
    redirect_to = redirect('lottery:games')
    if request.POST:
        if eval(is_detail_view):
            redirect_to = redirect('lottery:game-set-detail', game_set_id=games_sets_to_edit.first().id)
        form = forms.Form(request.POST)
        if form.is_valid():
            action = request.POST.get("action")
            games_sets_ids = [int(i) for i in request.POST.getlist("games-sets")]
            if games_sets_ids and action:
                action_name = gamesets.apply_action(games_sets_to_edit, [], action)
                messages.success(request, f"Conjuntos {action_name} com sucesso!")
        else:
            messages.error(request, f"Formulário Inválido! Tente novamente.")
    else:
        messages.error(request, f"Desculpe, ocorreu um erro inesperado! Tente novamente.")
    return redirect_to


@login_required
def send_game_sets(request, game_set_id):
    user_games_sets = gamesets.get_by_user(request.user)
    games_sets_to_send = request.POST.getlist("games-sets", [])
    games_sets_to_send = user_games_sets.filter(id__in=games_sets_to_send).prefetch_related("games")
    method = request.POST.get('method', '')
    redirect_to = redirect('lottery:games')
    if game_set_id:
        games_sets_to_send = [game_set_id]
        redirect_to = redirect('lottery:game-set-detail', result_id=game_set_id)
    if request.POST and not game_set_id:
        form = forms.Form(request.POST)
        if form.is_valid() and games_sets_to_send:
            pass
        else:
            games_sets_to_send = []
            messages.error(request, f"Formulário Inválido! Tente novamente.")
    if games_sets_to_send and method:
        if method == "email":
            gamesets.send_by_email(request.user, games_sets_to_send)
        elif method == "whatsapp":
            gamesets.send_by_whatsapp(request.user, games_sets_to_send, user_games_sets)
        messages.success(request, f"Conjuntos ENVIADOS com sucesso!" if len(
            games_sets_to_send) > 1 else f"Conjuntos ENVIADO com sucesso!")
    else:
        messages.error(request, f"Desculpe, ocorreu um erro inesperado! Tente novamente.")
    return redirect_to


@login_required
def export_collections(request):
    user_collections = collections.get_by_user(request.user)
    collections_to_export = request.POST.getlist("collections", [])
    collections_to_export = user_collections.filter(id__in=collections_to_export).prefetch_related("gamesets", "gamesets__games")
    if request.method == "POST":
        file_type = request.POST.get("file-type", "excel")
        handler = eval(f"collections.export_collections_by_{file_type}")
        data = handler(collections_to_export)
        response = HttpResponse(
            data["output"],
            content_type=data["content_type"],
        )
        response["Content-Disposition"] = f'attachment; filename={data["file_name"]}'
        return response


@login_required
def edit_collections(request):
    user_collections = collections.get_by_user(request.user)
    user_games_sets = gamesets.get_by_user(request.user)
    collections_to_edit = request.POST.getlist("collections", [])
    games_sets_ids = [int(i) for i in request.POST.getlist("gamesets", [])]
    is_detail_view = request.POST.get("is_detail", "False")
    collections_to_edit = user_collections.filter(id__in=collections_to_edit).prefetch_related("gamesets", "gamesets__games")
    redirect_to = redirect('lottery:games')
    action = request.POST.get("action")
    if request.POST:
        if eval(is_detail_view):
            if not action == "DELETAR":
                redirect_to = redirect('lottery:collection-detail', collection_id=collections_to_edit.first().id)
        form = forms.Form(request.POST)
        if form.is_valid():
            collections_ids = [int(i) for i in request.POST.getlist("collections")]
            if collections_ids and action:
                message = collections.apply_action(collections_to_edit, games_sets_ids, user_games_sets, action)
                messages.success(request, message)
        else:
            messages.error(request, f"Formulário Inválido! Tente novamente.")
    else:
        messages.error(request, f"Desculpe, ocorreu um erro inesperado! Tente novamente.")
    return redirect_to


@login_required
def send_collections(request):
    user_collections = collections.get_by_user(request.user)
    collections_to_send = request.POST.getlist("collections", [])
    collections_to_send = user_collections.filter(id__in=collections_to_send).prefetch_related("gamesets", "gamesets__games")
    method = request.POST.get('method', '')
    is_detail_view = request.POST.get("is_detail", "False")
    redirect_to = redirect('lottery:games')
    if request.POST:
        if eval(is_detail_view):
            redirect_to = redirect('lottery:collection-detail', collection_id=collections_to_send.first().id)
        form = forms.Form(request.POST)
        if form.is_valid():
            if collections_to_send and method:
                if method == "email":
                    collections.send_by_email(request.user, collections_to_send)
                elif method == "whatsapp":
                    collections.send_by_whatsapp(request.user, collections_to_send, user_collections)
                messages.success(request, f"Coleções ENVIADAS com sucesso!" if len(
                    collections_to_send) > 1 else f"Coleções ENVIADA com sucesso!")
            else:
                messages.error(request, f"Desculpe, ocorreu um erro inesperado! Tente novamente.")
        else:
            messages.error(request, f"Formulário Inválido! Tente novamente.")
    else:
        messages.error(request, f"Desculpe, ocorreu um erro inesperado! Tente novamente.")
    return redirect_to


@login_required
def games_generators(request):
    if request.is_ajax and request.method == "POST":
        form = forms.Form(request.POST)
        print(request.POST)
        if form.is_valid():
            data = request.POST
            lottery = Lottery.objects.get(name=data.get('lottery_name'))
            generator_name = data.get("generator")
            game_length = int(data.get('nPlayed'))
            removed_numbers, fixed_numbers = generators.parse_fixed_removed(data)
            filters = generators.parse_kwargs_filters(data)
            ts = time()
            games_generated, games_ids = [], []
            if generator_name == "simple":
                number_of_games = int(data.get("nJogos"))
                games_generated = generators.simple(lottery, game_length, number_of_games, removed_numbers,
                                                    fixed_numbers)
                games_ids = generators.get_or_create_by_dataframe(games_generated, lottery)
            elif generator_name == "smart":
                if eval(data.get("calcCombs")):
                    number_of_combs = generators.calc_combs(lottery, removed_numbers, fixed_numbers, filters)
                    return JsonResponse({"combs": number_of_combs}, status=200)
                else:
                    number_of_games = int(data.get("nJogos"))
                    games_generated, games_ids = generators.smart(lottery, number_of_games, removed_numbers,
                                                                  fixed_numbers, filters)
            else:
                pass
            tf = time()
            print(tf - ts)
            return JsonResponse({"jogos": games_generated.to_json(orient="split"), "ids": games_ids}, status=200)
        else:
            return JsonResponse({"error": form.errors}, status=400)
    return JsonResponse({"error": "Not found"}, status=400)


@login_required
def save_games_batch(request):
    if request.method == "POST":
        form = forms.Form(request.POST)
        print(request.POST)
        if form.is_valid():
            games_ids = request.POST.getlist("ids")
            games_set_name = request.POST.get("gameset-name")
            lottery = request.POST.get('lottery_name')
            instance = Gameset.objects.create(name=games_set_name, user=request.user,
                                              lottery=Lottery.objects.get(name=lottery))
            collections_list = request.POST.getlist('collection')
            game_length = int(request.POST.get('nPlayed'))
            gamesets.update_quantifiers(instance, games_ids, collections_list, game_length)
            instances = collections.get_by_user(request.user).filter(id__in=collections_list)
            collections.update_quantifiers(instances, games_ids)
            messages.success(request, f"Conjunto {games_set_name} salvo com sucesso!")
        return HttpResponseRedirect('jogos')


@login_required
def game_set_detail(request, game_set_id):
    games_set = Gameset.objects.get(id=game_set_id)
    if request.POST:
        form = forms.Form(request.POST)
        if form.is_valid():
            action = request.POST.get("action")
            games_ids = request.POST.getlist("games")
            action_name = gamesets.apply_action([game_set_id], games_ids, action, request.user)
            if action == "REMOVER":
                messages.success(request, f"Jogos {action_name} com sucesso!")
            else:
                messages.success(request, f"Conjunto {games_set.name} {action_name} com sucesso!")
            if action == "DELETAR":
                return redirect('lottery:games')
            return redirect('lottery:game-set-detail', game_set_id=game_set_id)

    ctx = {
        'gameset': games_set
    }
    return render(request, "platform/dashboard/game_set_detail.html", ctx)


@login_required
def collection_detail(request, collection_id):
    collection = Collection.objects.get(id=collection_id)
    user_games_sets = gamesets.get_by_user(request.user)
    user_games_sets = user_games_sets.filter(lottery=collection.lottery)
    user_games_sets = gamesets.check_in_collection(user_games_sets, collection)
    if request.POST:
        form = forms.Form(request.POST)
        if form.is_valid():
            action = request.POST.get("action")
            games_sets_ids = [int(i) for i in request.POST.getlist("gamesets")]
            action_name = collections.apply_action([collection_id], games_sets_ids, user_games_sets, action, request.user)
            if action == "DELETAR":
                messages.success(request, f"Coleção {collection.name} DELETADA com sucesso!")
                return redirect('lottery:games')
            elif action == "ADICIONAR":
                messages.success(request, f"Coleção {collection.name.capitalize()} ATUALIZADA com sucesso!")
            else:
                messages.success(request, f"Coleção {collection.name} {action_name} com sucesso!")
            return redirect('lottery:collection-detail', collection_id=collection_id)
    ctx = {
        'collection': collection,
        'gamesets': user_games_sets,
    }
    return render(request, "platform/dashboard/collection_detail.html", ctx)


@login_required
def draw_detail(request, name, number):
    draws = Draw.objects.filter(lottery__name=name)
    current_draw = draws.get(number=number)
    numbers_ranking = stats.numbers_ranking(draws.values_list("result"), current_draw.lottery)
    draw_numbers_ranking = numbers_ranking.loc[numbers_ranking.index.isin(current_draw.result)]
    parity_stats = stats.parity_balance(current_draw.result)
    latest_frequency = stats.latest_frequency_in_draws(current_draw.result, draws.order_by('-date').filter(number__lte=number))
    sequences = stats.sequences(current_draw.result)
    gaps = stats.gap(current_draw.result)
    primes = stats.nPrimeNumbers(current_draw.result)

    metadata = {
        'charts': {
            'parity_balance': parity_stats,
            'freq': latest_frequency,
        },
        'Sequência Máxima': ["Maior sequência de números consecutivos", max(sequences)],
        'Sequência Mínima': ["Menor sequência de números consecutivos", min(sequences)],
        'Salto Máximo': ["Maior salto de 2 números sorteados", max(gaps)],
        'Salto Mínimo': ["Maior salto de 2 números sorteados", min(gaps)],
        'Números Primos': ["Total de números primos", primes],
        'Soma': ["Soma de todos os números sorteados", sum(current_draw.result)],
        'Média': ["Média dos números sorteados", round(sum(current_draw.result)/len(current_draw.result), 2)]
    }
    ctx = {
        'draw': current_draw,
        'metadata': metadata,
        'total_freq': draw_numbers_ranking.sort_index(ascending=True)
    }
    return render(request, "platform/dashboard/draw_detail.html", ctx)


@login_required
def results_reports(request):
    lotteries_objs = Lottery.objects.all()
    user_results = results.get_by_user(request.user)
    user_collections = collections.get_by_user(request.user)
    last_results = user_results.order_by("-id")
    last_results = last_results[:5]
    total = user_results.aggregate(collections=Count('collection', distinct=True), games_sets=Sum("number_of_game_sets"), games=Sum("number_of_games"))
    ctx = {
        'lotteries': lotteries_objs,
        "results": user_results,
        "last_results": last_results,
        "collections": user_collections,
        "total": total
    }
    if user_results:
        messages.success(request, "Resultados carregados com sucesso!")
    else:
        messages.warning(request, "Não foram encontrados resultados. Gere seus relatórios abaixo!")
    return render(request, "platform/dashboard/results.html", ctx)


@login_required
def results_reports_detail(request, result_id):
    user_results = results.get_by_user(request.user)
    result = get_object_or_404(user_results, pk=result_id)
    money_balance = results.parse_money_balance_json(result.money_balance)
    points_by_games_sets = results.parse_points_by_games_sets_json(result, result.points_info["Conjuntos"])
    collection_historic = results.historic(user_results, result.collection)
    ctx = {
        "result": result,
        "money_balance": money_balance,
        "points_info": {
            "total": result.points_info["Total"],
            "winner_games": sum(result.points_info["Total"].values()),
            "by_games_sets": points_by_games_sets
        },
        "historic": collection_historic
    }
    return render(request, "platform/dashboard/result_detail.html", ctx)


@login_required
def delete_results_reports(request, result_id):
    user_results = results.get_by_user(request.user)
    if result_id:
        user_results.get(result_id).delete()
        messages.success(request, f"Resultado DELETADO com sucesso!")
    if request.POST and not result_id:
        form = forms.Form(request.POST)
        if form.is_valid():
            for result_id in request.POST.getlist("results"):
                result = user_results.filter(id=result_id)
                if result:
                    result.delete()
                    messages.success(request, f"Resultados DELETADOS com sucesso!")
        else:
            messages.error(request, f"Desculpe, ocorreu um erro inesperado! Tente novamente.")
    return redirect('lottery:results')


@login_required
def send_results_reports(request, result_id):
    user_results = results.get_by_user(request.user)
    results_to_send = request.POST.getlist("results", [])
    method = request.POST.get('method', '')
    redirect_to = redirect('lottery:results')
    if result_id:
        results_to_send = [result_id]
        redirect_to = redirect('lottery:result-detail', result_id=result_id)
    if request.POST and not result_id:
        form = forms.Form(request.POST)
        if form.is_valid() and results_to_send:
            pass
        else:
            results_to_send = []
            messages.error(request, f"Formulário Inválido! Tente novamente.")
    if results_to_send and method:
        if method == "email":
            results.send_by_email(request.user, results_to_send, user_results)
        elif method == "whatsapp":
            results.send_by_whatsapp(request.user, results_to_send, user_results)
        messages.success(request, f"Resultados ENVIADOS com sucesso!" if len(results_to_send) > 1 else f"Resultado ENVIADO com sucesso!")
    else:
        messages.error(request, f"Desculpe, ocorreu um erro inesperado! Tente novamente.")
    return redirect_to


@login_required
def export_results_reports(request):
    user_results = results.get_by_user(request.user)
    results_to_send = request.POST.getlist("results", [])
    results_to_send = user_results.filter(id__in=results_to_send)
    if request.method == "POST":
        file_type = request.POST.get("file-type", "excel")
        handler = eval(f"results.export_by_{file_type}")
        data = handler(results_to_send)

        response = HttpResponse(
            data["output"],
            content_type=data["content_type"],
        )
        response["Content-Disposition"] = f'attachment; filename={data["file_name"]}'
        return response


@login_required
def get_draws_numbers(request, name=''):
    draws = Draw.objects.filter(lottery__name=name).order_by("-date")
    draws_numbers = list(draws.values('number'))
    user_collections = collections.get_by_user(request.user)
    user_collections = user_collections.filter(lottery__name=name).values('id', 'name')
    data = {
        'draws': draws_numbers,
        'collections': list(user_collections)
    }
    return JsonResponse(data=data, status=200)


@login_required
def create_results_report(request):
    if request.method == "POST":
        form = forms.Form(request.POST)
        if form.is_valid():
            data = request.POST
            selected_collection = collections.get_by_user(request.user).get(id=data.get("collection_id"))
            user_games_sets = gamesets.get_by_user(request.user).prefetch_related("collections")
            games_sets_in_collection = user_games_sets.filter(collections=selected_collection)
            games_sets_actives = data.get("active", True)
            filtered_games_sets = games_sets_in_collection.filter(isActive=games_sets_actives)
            selected_draw = Draw.objects.get(lottery__name=data.get("lottery_name"), number=data.get("draw"))
            total_scores = results.check_scores_in_draw(selected_draw, filtered_games_sets)
            prizes_balance = results.check_prizes_in_draw(selected_draw, total_scores)
            file_url, result_obj = results.create_text_report_file(selected_draw, total_scores,
                                                                   selected_collection,
                                                                   prizes_balance)
            data = {
                'draw': model_to_dict(selected_draw),
                'filepath': file_url,
                'total_balance': prizes_balance["Total Geral"],
                'result_id': result_obj.id
            }
            data['draw']['date'] = format_date(data['draw']['date'], "dd/MM/yyyy", "pt_br")
            return JsonResponse(data=data, status=200)
        return JsonResponse(data={"message": "Formulário Inválido! Tente novamente."}, status=400)
    return JsonResponse(data={"message": "Erro na requisição! Tente novamente."}, status=500)


@login_required
def export_results_reports_games(request, result_id):
    user_results = results.get_by_user(request.user)
    result = user_results.get(id=result_id)
    if request.method == "POST":
        print(request.POST)
        if result:
            games_ids = request.POST.getlist("games", [])
            games_to_export = Game.objects.filter(id__in=games_ids)
            file_type = request.POST.get("file-type", "excel")
            handler = eval(f"results.export_results_games_by_{file_type}")
            data = handler(games_to_export)

            response = HttpResponse(
                data["output"],
                content_type=data["content_type"],
            )
            response["Content-Disposition"] = f'attachment; filename={data["file_name"]}'
            return response


@login_required
def create_game_set_from_result(request, result_id):
    if request.method == "POST":
        result = results.get_by_user(request.user).filter(id=result_id)
        if result:
            game_set_name = request.POST.get("gameset-name")
            print(game_set_name, request.POST)
            is_active = int(request.POST.get("is-active"))
            games_ids = request.POST.getlist("games")
            if game_set_name and games_ids:
                games_to_include = Game.objects.filter(id__in=games_ids)
                game_set = Gameset.objects.create(name=game_set_name,
                                                  user=request.user,
                                                  lottery=result[0].lottery,
                                                  numberOfGames=games_to_include.count(),
                                                  gameLength=len(games_to_include[0].arrayNumbers),
                                                  isActive=bool(is_active)
                                                  )
                game_set.games.set(games_to_include)
                game_set.save()
                messages.success(request, "Conjunto criado com sucesso!")
                return redirect('lottery:game-set-detail', game_set_id=game_set.id)
            messages.error(request, "Ocorreu algum erro inesperado. Tente novamente!")
            return redirect('lottery:result-detail', result_id=result_id)
    messages.error(request, "Ocorreu algum erro inesperado. Tente novamente!")
    return redirect('lottery:result-detail', result_id=result_id)


@login_required
def get_combinations(request):
    combs_size = request.GET.get("combs-size")
    lottery = request.GET.get("lottery")
    combs = Combinations.objects.filter(lottery=lottery, n=combs_size)
    combs = combs.order_by("-repetitions")
    combs_filtered = combs.exclude(repetitions=0)[:5000]
    data = {
        "combs": list(combs_filtered.values("numbers", "repetitions")),
        "total": combs.count()
    }
    return JsonResponse(data, status=200)


@login_required
def profile(request):
    return render(request, "platform/dashboard/profile.html")


class CustomLoginView(auth_views.LoginView):
    template_name = "platform/auth/login.html"


class CustomLogoutView(auth_views.LogoutView):
    template_name = "platform/auth/login.html"


@login_required
def billing(request):
    return render(request, "platform/dashboard/billing.html")


def register(request):
    form = CustomUserCreationForm(request.POST)
    if request.method == "POST":
        new_user = CustomUserCreationForm(request.POST)
        if new_user.is_valid():
            new_user.save()
            messages.success(request, "Usuário cadastrado com sucesso!")
            return redirect('lottery:dashboard')
    ctx = {"form": form}
    return render(request, "platform/auth/register.html", ctx)