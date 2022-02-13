import os.path
from functools import reduce

from django.shortcuts import render, redirect
from lottery.forms import CreateCollectionForm, UploadCollectionForm
from lottery.models import Lottery, LOTTERY_CHOICES, Game, Draw, Gameset, Collection
from django import forms
from django.core import serializers
from django.http import JsonResponse
from django.db.models import Sum, F, Q, Case, When
import pandas as pd
import numpy as np
import random
from lottery.backend.Jogos import generators
from lottery.backend.Loterias import stats
from lottery.backend.functions import stats
from lottery.forms import CustomUserCreationForm, LoginForm
from django.forms.models import model_to_dict
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import User
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.http import HttpResponseRedirect, HttpResponse
from time import time
from babel.dates import format_date
import json
import io
from django.core.files.storage import default_storage
from django.core.files import File
from django.core.files.base import ContentFile
from django.conf import settings
import math
# Create your views here.

def reverseMapping(jogo, loto):
    lottery = Lottery.objects.get(name=loto)
    print(lottery.numbersRangeLimit)
    jogo0 = np.zeros(lottery.numbersRangeLimit)
    jogo = np.array(jogo)
    for number in jogo:
        jogo0[number-1] = 1
    number = 0
    for pos,value in enumerate(jogo0):
        number += value*math.pow(2,pos)
    return number


@login_required
def createCollection(request):
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
    return render(request, "plataform/dashboard/dashboard.html")



@login_required
def loterias(request):
    LOTTERY_CHOICES = [
        ("lotofacil", "Lotofácil"),
        ("diadesorte", "Dia de Sorte"),
        ("megasena", "Mega Sena"),
    ]
    draws = Draw.objects.all()
    draws = draws.annotate(loto_name=F("lottery__name"))
    ctx = {
        'lototypes': LOTTERY_CHOICES,
        'lastDraws': draws.order_by('lottery_id', '-date').distinct('lottery_id')[:3],
    }
    return render(request, "plataform/dashboard/loterias.html", ctx)


@login_required
def loteriasDetail(request, name=''):
    draws = Draw.objects.all()
    draws = draws.annotate(loto_name=F("lottery__name"))
    last_draws = draws.order_by('lottery_id', '-date').distinct('lottery_id')[:3]
    draws = draws.order_by('lottery_id', 'number').filter(lottery__name=name)
    lottery = draws[0].lottery
    ranking = stats.numbers_ranking(draws)
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
    return render(request, "plataform/dashboard/loteriaDetail.html", ctx)



@login_required
def jogos(request):
    user = request.user
    userGamesets = user.gamesets.all().order_by('-createdAt')
    lastGamesets = userGamesets[:5]
    userCollections = user.collections.all().order_by('-createdAt')
    userCollections = userCollections.annotate(loto_name=F("lottery__name"))
    lastCollections = userCollections[:5]
    collectionForm = CreateCollectionForm()
    uploadCollectionForm = UploadCollectionForm()

    if request.POST:
        form = forms.Form(request.POST)
        if form.is_valid():
            action = request.POST.get("action")
            gamesets_ids = request.POST.getlist("gamesets")
            gamesets_ids = [int(i) for i in gamesets_ids]
            collections_ids = request.POST.getlist("collections")
            collections_ids = [int(i) for i in collections_ids]
            print(request.POST)
            action_name = "MODIFICADOS"
            if gamesets_ids:
                for gameset in userGamesets.filter(id__in=gamesets_ids):
                    print(gameset.id, action)
                    if action == "ATIVAR":
                        action_name = "ATIVADOS"
                        gameset.isActive = True
                        gameset.save()
                    elif action == "DESATIVAR":
                        action_name = "DESATIVADOS"
                        gameset.isActive = False
                        gameset.save()
                    elif action == "DELETAR":
                        action_name = "DELETADOS"
                        gameset.delete()
                messages.success(request, f"Conjuntos {action_name} com sucesso!")
            if collections_ids:
                for collection in userCollections.filter(id__in=collections_ids):
                    print(collection.id, action)
                    if action == "DELETAR":
                        action_name = "DELETADOS"
                        collection.delete()
                messages.success(request, f"Coleções {action_name} com sucesso!")
            return redirect('lottery:jogos')
    gamesetsData = {
        'gamesets': userGamesets,
        'lastGamesets': lastGamesets,
    }

    collectionsData = {
        'collections': userCollections,
        'lastCollections': lastCollections,
        'totalGamesets': userGamesets.count(),
        'totalCollections': userCollections.count(),
        'totalGames': userGamesets.aggregate(sum=Sum('numberOfGames'))
    }

    ctx={
        'lototypes': LOTTERY_CHOICES,
        'gamesetsData': gamesetsData,
        'collectionsData': collectionsData,
        'collectionForm': collectionForm,
        'uploadCollectionForm': uploadCollectionForm,
    }
    print(ctx)
    return render(request, "plataform/dashboard/jogos.html", ctx)


@login_required
def generator(request):
    if request.is_ajax and request.method == "POST":
        form = forms.Form(request.POST)
        print(request.POST)
        if form.is_valid():
            data = dict(form.data)
            nRemoved = [int(i) for i in data.get('nRemoved', [])]
            nFixed = [int(i) for i in data.get('nFixed', [])]
            nPlayed = int(data['nPlayed'][0])
            loto = data['lototype'][0]
            generator = data["generator"][0]
            filters_keys = ["nPrimes", "maxSeq", "minSeq", "maxGap", "isOdd"]
            filters = {}
            games_ids = []
            ts = time()
            if generator == "simple":
                nJogos = int(data['nJogos'][0])
                jogos = generators.simple(loto, nPlayed, nJogos, nRemoved, nFixed)
                print(jogos.head())
                for index, jogo in jogos.iterrows():
                    game = Game.objects.get(arrayNumbers=jogo.to_list())
                    games_ids.append(game.id)
            else:
                for key in filters_keys:
                    try:
                        filter_value = data.get(key)[0]
                    except (KeyError, TypeError):
                        pass
                    else:
                        if filter_value:
                            filters[key] = filter_value
                if eval(data.get("calcCombs")[0]):
                    n_combs = generators.calc_combs(loto, nRemoved, nFixed, filters).count()
                    print(n_combs)
                    return JsonResponse({"combs": n_combs}, status=200)
                else:
                    nJogos = int(data['nJogos'][0])
                    jogos = generators.smart(loto, nJogos, nRemoved, nFixed, filters)
                    data = []
                    for index, jogo in jogos.iterrows():
                        data.append(jogo["arrayNumbers"])
                        games_ids.append(jogo["id"])
                    jogos = pd.DataFrame(data)
            print(jogos.head())
            print(games_ids)
            tf = time()
            print(tf - ts)

            return JsonResponse({"jogos": jogos.to_json(orient="split"), "ids": games_ids}, status=200)
        else:
            print('error1')
            return JsonResponse({"error": form.errors}, status=400)
    print('error')
    return JsonResponse({"error": "Not found"}, status=400)


@login_required
def save_games_batch(request):
    if request.method == "POST":
        ts = time()
        form = forms.Form(request.POST)
        print(request.POST)
        if form.is_valid():
            ids = request.POST.getlist("ids")
            gameset = request.POST.get("gameset-name")
            lottery = request.POST.get('lototype')
            instance = Gameset.objects.create(name=gameset, user=request.user,
                                              lottery=Lottery.objects.get(name=lottery))
            games_list = []
            collections_list = request.POST.getlist('collection')
            nPlayed = 0
            for id in ids:
                game = Game.objects.get(pk=id)
                games_list.append(game.id)
                nPlayed = len(game.arrayNumbers)
            instance.games.set(games_list)
            instance.numberOfGames = len(games_list)
            instance.gameLength = nPlayed
            instance.collections.set(collections_list)
            instance.save()
            collections = Collection.objects.filter(id__in=collections_list)
            for instance in collections:
                instance.numberOfGames += len(games_list)
                instance.numberOfGamesets += 1
                instance.save()
            tf = time()
            print(tf - ts)
            messages.success(request, f"Conjunto {gameset} salvo com sucesso!")
        return HttpResponseRedirect('jogos')


@login_required
def conjuntosDetail(request, gameset_id):
    gameset = Gameset.objects.get(id=gameset_id)
    #gameset.numberOfGames = gameset.games.all().count()
    if request.POST:
        form = forms.Form(request.POST)
        if form.is_valid():
            action = request.POST.get("action")
            games_ids = request.POST.getlist("games")
            print(request.POST)
            if games_ids:
                for game_id in games_ids:
                    gameset.games.remove(int(game_id))
                print(len(games_ids))
                gameset.numberOfGames -= len(games_ids)
                messages.success(request, f"Jogos REMOVIDOS com sucesso!")
                gameset.save()
            if action == "ATIVAR":
                gameset.isActive = True
                gameset.save()
                messages.success(request, f"Conjunto {gameset.name} ATIVADO com sucesso!")
            elif action == "DESATIVAR":
                gameset.isActive = False
                gameset.save()
                messages.success(request, f"Conjunto {gameset.name} DESATIVADO com sucesso!")
            elif action == "DELETAR":
                gameset.delete()
                messages.success(request, f"Conjunto {gameset.name} DELETADO com sucesso!")
                return redirect('lottery:jogos')
            return redirect('lottery:conjunto-detail', gameset_id=gameset_id)

    ctx = {
        'gameset': gameset
    }
    return render(request, "plataform/dashboard/conjuntosDetail.html", ctx)


@login_required
def colecoesDetail(request, collection_id):
    collection = Collection.objects.get(id=collection_id)
    gamesets = Gameset.objects.filter(lottery=collection.lottery)
    gamesets = gamesets.prefetch_related("collections")
    print(gamesets.count())
    gamesets = gamesets.annotate(include=F("isActive"))
    for gameset in gamesets:
        if collection in gameset.collections.all():
            gameset.include = True
        else:
            gameset.include = False
    if request.POST:
        form = forms.Form(request.POST)
        if form.is_valid():
            action = request.POST.get("action")
            if action == "DELETAR":
                messages.success(request, f"Conjunto {collection.name} DELETADO com sucesso!")
                collection.delete()
                return redirect('lottery:jogos')
            elif action == "ADICIONAR":
                gamesets_ids = request.POST.getlist("gamesets")
                gamesets_ids = [int(i) for i in gamesets_ids]
                print(gamesets_ids)
                print(gamesets)
                collection.numberOfGamesets = 0
                collection.numberOfGames = 0
                for gameset in gamesets:
                    if gameset.id in gamesets_ids:
                        collection.gamesets.add(gameset.id)
                        collection.numberOfGamesets += 1
                        collection.numberOfGames += gameset.numberOfGames
                    else:
                        collection.gamesets.remove(gameset.id)
                messages.success(request, f"Coleção {collection.name.capitalize()} ATUALIZADA com sucesso!")
                collection.save()
                return redirect('lottery:colecao-detail', collection_id=collection_id)
    ctx = {
        'collection': collection,
        'gamesets': gamesets,
    }
    return render(request, "plataform/dashboard/colecoesDetail.html", ctx)


@login_required
def concursosDetail(request, name, number):
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
    return render(request, "plataform/dashboard/concursosDetail.html", ctx)


@login_required
def relatorios(request):
    return render(request, "plataform/dashboard/relatorios.html")


@login_required
def profile(request):
    return render(request, "plataform/dashboard/profile.html")


class CustomLoginView(auth_views.LoginView):
    template_name = "plataform/auth/login.html"


class CustomLogoutView(auth_views.LogoutView):
    template_name = "plataform/auth/login.html"


def register(request):
    form = CustomUserCreationForm(request.POST)
    if request.method == "POST":
        new_user = CustomUserCreationForm(request.POST)
        if new_user.is_valid():
            new_user.save()
            messages.success(request, "Usuário cadastrado com sucesso!")
            return redirect('lottery:dashboard')
    ctx = {"form": form}
    return render(request, "plataform/auth/register.html", ctx)


@login_required
def billing(request):
    return render(request, "plataform/dashboard/billing.html")

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
    lottery = data.get("lototype2")
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