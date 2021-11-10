from functools import reduce

from django.shortcuts import render
from lottery.forms import GameGeneratorForm
from lottery.models import Lottery, LOTTERY_CHOICES, Game, Draw, Gameset, Collection
from django import forms
from django.core import serializers
from django.http import JsonResponse
from django.db.models import Sum
import pandas as pd
import numpy as np
import random
from lottery.backend.Jogos import generators
from time import time
import json
import math
# Create your views here.

def reverseMapping(jogo):
    jogo0 = np.zeros(25)
    jogo = np.array(jogo)
    for number in jogo:
        jogo0[number-1] = 1
    number = 0
    for pos,value in enumerate(jogo0):
        number += value*math.pow(2,pos)
    return number


def landing(request):
    return render(request, "landing/pages/about-us.html")


def geneor(request, loto):
    loto = Lottery.objects.get(id=loto)
    choicesNPlayed = [i for i in loto.possiblesChoicesRange]
    choices = [i for i in range(1, loto.numbersRangeLimit + 1)]
    cols = 1
    if loto.name == "lotofacil":
        cols = 5
    if request.method == "POST":
        form = forms.Form(request.POST)
        print(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
    context = {
        "nPlayed": choicesNPlayed,
        "nFixed": choices,
        "nRemoved": choices,
        "cols": cols,
    }
    return render(request, "lottery/generator.html", context)


def dashboard(request):
    return render(request, "plataform/dashboard/dashboard.html")


def loterias(request):
    ctx = {
        'lototypes': LOTTERY_CHOICES}
    return render(request, "plataform/dashboard/loterias.html", ctx)


def jogos(request):
    user = request.user
    userGamesets = user.gamesets.all()
    lastGamesets = userGamesets.order_by('-createdAt')[:5]
    userCollections = user.collections.all()
    lastCollections = userCollections.order_by('-createdAt')[:5]

    gamesetsData = {
        'gamesets': userGamesets,
        'lastGamesets': lastGamesets,
    }

    collectionsData = {
        'collections': userCollections,
        'lastCollecions': lastCollections,
        'totalGamesets': userGamesets.count(),
        'totalCollections': userCollections.count(),
        'totalGames': userGamesets.aggregate(sum=Sum('numberOfGames'))
    }

    ctx={
        'lototypes': LOTTERY_CHOICES,
        'gamesetsData': gamesetsData,
        'collectionsData': collectionsData
    }
    print(ctx)
    return render(request, "plataform/dashboard/jogos.html", ctx)


def generator(request):
    if request.is_ajax and request.method == "POST":
        form = forms.Form(request.POST)
        print(request.POST)
        if form.is_valid():
            data = dict(form.data)
            nRemoved = [int(i) for i in data.get('nRemoved', [])]
            nFixed = [int(i) for i in data.get('nFixed', [])]
            gameset = data.get('gameset-name')[0]
            collection = data.get('collection')
            loto=data['lototype'][0]
            jogos = generators.simpleGenerator(loto, int(data['nPlayed'][0]), int(data['nJogos'][0]), nRemoved, nFixed)
            print(jogos.head())
            gamesList = []
            ts = time()
            games = Game.objects.filter(lottery__name=loto)
            for index, jogo in jogos.iterrows():
                code = reverseMapping(jogo)
                game = games.get(gameCode=code)
                gamesList.append(game.id)
            tf = time()
            print(tf-ts)
            instance = Gameset.objects.create(name=gameset, user=request.user,
                       lottery=Lottery.objects.get(name=loto))
            instance.games.set(gamesList)
            instance.numberOfGames = len(jogos)
            instance.gameLength = data.get('nPlayed')[0]
            instance.collections.set(collection)
            instance.save()
            collections = Collection.objects.filter(id__in=collection)
            for instance in collections:
                instance.numberOfGames += len(jogos)
                instance.numberOfGamesets += 1
                instance.save()
            return JsonResponse({"jogos": jogos.to_json(orient="split")}, status=200)
        else:
            print('error1')
            return JsonResponse({"error": form.errors}, status=400)
    print('error')
    return JsonResponse({"error": "Not found"}, status=400)


def conjuntosDetail(request, gameset_id):
    gameset = Gameset.objects.filter(id=gameset_id)[0]
    ctx = {
        'gameset': gameset
    }
    return render(request, "plataform/dashboard/conjuntosDetail.html", ctx)


def colecoesDetail(request, collection_id):
    collection = Collection.objects.filter(id=collection_id)[0]
    ctx = {
        'collection': collection
    }

    return render(request, "plataform/dashboard/colecoesDetail.html", ctx)


def concursosDetail(request, id):
    return render(request, "plataform/dashboard/concursosDetail.html")

def relatorios(request):
    return render(request, "plataform/dashboard/relatorios.html")


def profile(request):
    return render(request, "plataform/dashboard/profile.html")


def signin(request):
    return render(request, "plataform/auth/sign-in.html")


def signup(request):
    return render(request, "plataform/auth/sign-up.html")


def billing(request):
    return render(request, "plataform/dashboard/billing.html")
