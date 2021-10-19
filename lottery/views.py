from django.shortcuts import render
from lottery.forms import GameGeneratorForm
from lottery.models import Lottery, LOTTERY_CHOICES
from django import forms
from django.core import serializers
from django.http import JsonResponse
import pandas as pd
import numpy as np
import random
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


def simpleGenerator(nPlayed, nJogos, removedNumbers, fixedNumbers):
    """ Gerador simples. Sem filtros específicos

    :param nPlayed: Quantidade de números escolhidos por jogo
    :param nJogos: Número de jogos a ser criado
    :param removedNumbers: Números removidos
    :param fixedNumbers: Números fixados
    :return: None. Cria n jogos pedidos pelo user
    """
    nFixed = len(fixedNumbers)
    nPossibles = range(1, 26)
    nPlayed = nPlayed
    jogos = [0]
    numbersAllowed = np.array(np.setdiff1d(np.array(nPossibles), removedNumbers))
    numbersAllowed = np.setdiff1d(numbersAllowed, fixedNumbers)

    cont = 0
    while cont < nJogos:
        numbersAllowedCopy = list(numbersAllowed)
        random.shuffle(numbersAllowedCopy)
        np.random.RandomState(cont)
        jogo = np.zeros(nPlayed - nFixed)
        for i in range(0, jogo.size):
            number = np.random.choice(numbersAllowedCopy, 1)
            jogo[i] = number
            numbersAllowedCopy.remove(number)

        jogo = np.union1d(jogo, fixedNumbers).astype("int8")
        jogo = list(jogo)
        if jogo in jogos:
            continue
        else:
            jogos.append(jogo)
            cont += 1

    jogos.pop(0)
    return pd.DataFrame(jogos)


def generator(request):
    if request.is_ajax and request.method == "POST":
        form = forms.Form(request.POST)
        print(request.POST)
        if form.is_valid():
            data = dict(form.data)
            nRemoved = [int(i) for i in data['nRemoved']]
            nFixed = [int(i) for i in data['nFixed']]
            jogos = simpleGenerator(int(data['nPlayed'][0]), int(data['nJogos'][0]), nRemoved, nFixed)
            print(jogos.head())
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
