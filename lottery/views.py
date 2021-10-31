from django.shortcuts import render
from lottery.forms import GameGeneratorForm
from lottery.models import Lottery, LOTTERY_CHOICES, Game, Draw, Gameset, Collection
from django import forms
from django.core import serializers
from django.http import JsonResponse
import pandas as pd
import numpy as np
import random
from lottery.backend.Jogos import generators
from time import time
import json
# Create your views here.


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
    return render(request, "plataform/dashboard/loterias.html")


def jogos(request):
    if request.method == "POST":
        print(request.POST)
    print(request)
    loto = Lottery.objects.get(id=1)
    choicesNPlayed = [i for i in loto.possiblesChoicesRange]
    choices = [i for i in range(1, loto.numbersRangeLimit + 1)]
    cols = 10
    if loto.name == "lotofacil":
        cols = 5
    if request.method == "POST":
        form = forms.Form(request.POST)
        print(request.POST)
        if form.is_valid():
            print(form.cleaned_data)

    ctx={
        'lototypes': LOTTERY_CHOICES,
        "nPlayed": choicesNPlayed,
        "nFixed": choices,
        "nRemoved": choices,
        "cols": cols,
    }
    return render(request, "plataform/dashboard/jogos.html", ctx)


def generator(request):
    if request.is_ajax and request.method == "POST":
        form = forms.Form(request.POST)
        print(request.POST)
        if form.is_valid():
            data = dict(form.data)
            nRemoved = [int(i) for i in data['nRemoved']]
            nFixed = [int(i) for i in data['nFixed']]
            jogos = generators.simpleGenerator(data['lototype'][0], int(data['nPlayed'][0]), int(data['nJogos'][0]), nRemoved, nFixed)
            print(jogos.head())
            gamesList = []
            ts = time()
            for index, jogo in jogos.iterrows():
                game = Game.objects.get(arrayNumbers=jogo.to_list())
                gamesList.append(game.id)
            tf = time()
            print(tf-ts)
            instance = GamesGroup.objects.create(name='teste', user=request.user,
                       lottery=Lottery.objects.get(name=data['lototype'][0]))
            instance.games.set(gamesList)
            return JsonResponse({"jogos": jogos.to_json(orient="split")}, status=200)
        else:
            print('error1')
            return JsonResponse({"error": form.errors}, status=400)
    print('error')
    return JsonResponse({"error": "Not found"}, status=400)


def conjuntosDetail(request, id):
    return render(request, "plataform/dashboard/conjuntosDetail.html")


def colecoesDetail(request, id):
    return render(request, "plataform/dashboard/colecoesDetail.html")

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
