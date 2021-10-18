from django.shortcuts import render
from lottery.forms import GameGeneratorForm
from lottery.models import Lottery, LOTTERY_CHOICES
from django import forms

# Create your views here.


def landing(request):
    return render(request, "landing/pages/about-us.html")


def generator(request, loto):
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
