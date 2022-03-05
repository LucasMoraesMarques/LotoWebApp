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
            user_collections = collections.all(request.user)
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
    user_games_sets = gamesets.all(request.user)
    last_games_sets = gamesets.historic(request.user)
    user_collections = collections.all(request.user)
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
            instances = collections.all(request.user).filter(id__in=collections_list)
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
    user_games_sets = gamesets.all(request.user)
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
    user_collections = collections.all(request.user)
    last_results = user_results.order_by("lottery", "-draw__date")
    last_results = last_results[:5]
    total = user_results.aggregate(collections=Count('collection', distinct=True), games_sets=Sum("number_of_game_sets"), games=Sum("number_of_games"))
    ctx = {
        'lotteries': lotteries_objs,
        "results": user_results,
        "last_results": last_results,
        "collections": user_collections,
        "total": total
    }
    print(ctx)
    return render(request, "platform/dashboard/results.html", ctx)


@login_required
def results_reports_detail(request, result_id):
    user_results = results.get_by_user(request.user)
    result = get_object_or_404(user_results, pk=result_id)
    money_balance = results.parse_money_balance_json(result.money_balance)
    points_by_games_sets = results.parse_points_by_games_sets_json(result, result.points_info["Conjuntos"])
    ctx = {
        "result": result,
        "money_balance": money_balance,
        "points_info": {
            "total": result.points_info["Total"],
            "winner_games": sum(result.points_info["Total"].values()),
            "by_games_sets": points_by_games_sets
        }

    }
    return render(request, "platform/dashboard/result_detail.html", ctx)


@login_required
def profile(request):
    return render(request, "platform/dashboard/profile.html")


class CustomLoginView(auth_views.LoginView):
    template_name = "platform/auth/login.html"


class CustomLogoutView(auth_views.LogoutView):
    template_name = "platform/auth/login.html"


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


@login_required
def billing(request):
    return render(request, "platform/dashboard/billing.html")


@login_required
def get_draws_numbers(request, name=''):
    draws = Draw.objects.filter(lottery__name=name).order_by("-date")
    draws_numbers = list(draws.values('number'))
    user_collections = collections.all(request.user)
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
            selected_collection = collections.all(request.user).get(id=data.get("collection_id"))
            user_games_sets = gamesets.all(request.user).prefetch_related("collections")
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
                'total_balance': prizes_balance["Total Geral"]
            }
            data['draw']['date'] = format_date(data['draw']['date'], "dd/MM/yyyy", "pt_br")
            info = {
                "user1":[{"SUBJECT": "TESTE",
                 "BODY": "TESTE",
                 "FROM": "lucasmoraes@gmail.com",
                 "TO": [request.user.email],
                 "TEMPLATE": "emails/template1.html",
                "FILES": (result_obj.report_file,)}],

            }
            #email_sending.custom_send_email(info)
            return JsonResponse(data=data, status=200)


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

