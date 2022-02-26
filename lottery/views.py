from django.shortcuts import render, redirect
from lottery.forms import CreateCollectionForm, UploadCollectionForm
from lottery.models import Lottery, LOTTERY_CHOICES, Game, Draw, Gameset, Collection, Combinations
from django import forms
from django.http import JsonResponse
from django.db.models import Sum, F, Q, Case, When
import pandas as pd
from lottery.backend.games import generators, gamesets, collections
from lottery.backend.functions import stats
from lottery.forms import CustomUserCreationForm, LoginForm
from django.forms.models import model_to_dict
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.http import HttpResponseRedirect, HttpResponse
from time import time
from babel.dates import format_date
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


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
            collection = form.save(request.user)
            data = {
                    'name': collection.name,
                    'id': collection.id,
                    'lottery': str(collection.lottery)
                }
            return JsonResponse(data=data, status=200)
        return JsonResponse(data={'error': "Um erro inesperado impediu a criação da coleção. Tente novamente."}, status=400)


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
    even = odd = 0
    freq = {i:0 for i in current_draw.result}
    totalFreq = {i: 0 for i in current_draw.result}
    for value in current_draw.result:
        if value % 2 == 0:
            even += 1
        else:
            odd += 1

        for draw in draws.order_by('-date').filter(number__lte=number):
            if value in draw.result:
                freq[value] += 1
            else:
                break
    for draw in draws.order_by('number'):
        for value in current_draw.result:
            if value in draw.result:
                totalFreq[value] += 1
    seq = stats.sequences(current_draw.result)
    gaps = stats.gap(current_draw.result)
    primes = stats.nPrimeNumbers(current_draw.result)


    metadata = {
        'charts': {
            'even': even,
            'odd': odd,
            'freq': freq,
        },
        'Sequência Máxima': ["Maior sequência de números consecutivos", max(seq)],
        'Sequência Mínima': ["Menor sequência de números consecutivos", min(seq)],
        'Salto Máximo': ["Maior salto de 2 números sorteados", max(gaps)],
        'Salto Mínimo': ["Maior salto de 2 números sorteados", min(gaps)],
        'Números Primos': ["Total de números primos", primes],
        'Soma': ["Soma de todos os números sorteados", sum(current_draw.result)],
        'Média': ["Média dos números sorteados", round(sum(current_draw.result)/len(current_draw.result),2)]
    }
    ctx = {
        'draw': current_draw,
        'metadata': metadata,
        'totalFreq': totalFreq
    }
    return render(request, "platform/dashboard/draw_detail.html", ctx)


@login_required
def results(request):
    return render(request, "platform/dashboard/results.html")


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
def get_selected_draw(request):
    user = request.user
    if request.method == 'GET':
        lottery = request.GET.get('lottery', 0)
        draws = list(Draw.objects.filter(lottery__name=lottery).order_by("-date").values('number'))
        collections = list(user.collections.filter(lottery__name=lottery).values('id', 'name'))
        data = {
            'draws': draws,
            'collections': collections
        }
        return JsonResponse(data=data, status=200)
    if request.method == "POST":
        form = forms.Form(request.POST)
        if form.is_valid():
            data = request.POST
            data = check_collection_in_draw(data)
            return JsonResponse(data=data, status=200)


def check_collection_in_draw(data):
    col_is_active = data.get("active")
    collection = Collection.objects.get(id=data.get("collection_id"))
    lottery = data.get("lottery_id_results")
    draw = Draw.objects.get(number=data.get("draw"), lottery__name=lottery)
    lottery = Lottery.objects.get(name=lottery)
    file_url, total_balance = check_results(draw, lottery, collection)
    data = {
        'draw': model_to_dict(draw),
        'results': model_to_dict(collection, fields=[field.name for field in collection._meta.fields]),
        'filepath': file_url,
        'total_balance': total_balance
    }
    data['draw']['date'] = format_date(data['draw']['date'], "dd/MM/yyyy", "pt_br")
    return data


def check_results(draw, lottery, collection):
    result = draw.result
    print(result)
    filename = f'{collection.name.replace(" ", "_")}_{draw.number}.txt'
    restext = f"Resultado referente ao concurso nº {draw.number} da {lottery.name} " \
              f"realizado no dia {format_date(draw.date, 'dd/MM/yyyy', 'pt_br')}\n"
    lines = []
    lines.append(restext)
    gamesets = collection.gamesets.all()
    print(gamesets)
    total_balance = {
        'Premiacao': 0,
        'Valor Gasto': 0,
        'Saldo': 0,
        'Numero de Jogos': collection.numberOfGames
    }
    for gameset in gamesets:
        lines.append(f"\n\n{gameset.name:=^20}\n")
        games = gameset.games.all()
        interval = lottery.possiblesPointsToEarn
        scores = acertos(result, games, interval)
        scores['Premiacao'] = 0
        scores['Valor Gasto'] = gameset.numberOfGames * lottery.possiblesPricesRange[
            gameset.gameLength - lottery.possiblesChoicesRange[0]]
        for acerto in interval:
            for faixa, data in draw.metadata[0].items():
                print(faixa, data)
                if int(data['descricaoFaixa'].split(" ")[0]) == acerto:
                    scores['Premiacao'] += scores[f'Total {acerto}'] * data['valorPremio']
        scores['Saldo'] = scores['Premiacao'] - scores['Valor Gasto']
        total = [f'Total {i}' for i in interval]
        moneyBalance = ['Premiacao', 'Valor Gasto', 'Saldo']
        for value in total:
            lines.append(f"\n{value}: {scores[value]}")

        for value in moneyBalance:
            lines.append(f"\n{value}: R$ {scores[value]:,.2f}")
            total_balance[value] += scores[value]
        lines.append('\n')
        for k, v in scores.items():
            if k not in total and k not in moneyBalance:
                lines.append(f"\n{k}: {v} acertos")

    default_storage.save(filename, ContentFile("".join(lines)))
    return filename, total_balance


def acertos(result, games, interval):
    scores = {f'Total {i}': 0 for i in interval}
    i = 1
    for game in games:
        score = len(set(game.arrayNumbers) & set(result))
        scores[f"Jogo {i}"] = score
        i += 1
        if score in interval:
            scores[f'Total {score}'] += 1
    return scores


@login_required
def get_combinations(request):
    print(request.GET)
    combs_size = request.GET.get("combs-size")
    lottery = request.GET.get("lottery")
    combs = Combinations.objects.filter(lottery=lottery, n=combs_size)
    combs = combs.order_by("-repetitions")
    combs_filtered = combs.exclude(repetitions=0)[:5000]
    data = {
        "combs": list(combs_filtered.values("numbers", "repetitions")),
        "total": combs.count()
    }
    print(combs_filtered.count())
    return JsonResponse(data, status=200)
