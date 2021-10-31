"""LotoWebApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from lottery import views

app_name = "lottery"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("loterias", views.loterias, name="loterias"),
    path("loterias/concursos/<int:id>", views.concursosDetail, name="concurso-detail"),
    path("jogos", views.jogos, name="jogos"),
    path("jogos/conjuntos/<int:id>", views.conjuntosDetail, name="conjunto-detail"),
    path("jogos/colecoes/<int:id>", views.colecoesDetail, name="colecao-detail"),
    path("jogos/generator", views.generator, name="generator"),
    path("relatorios", views.relatorios, name="relatorios"),
    path("profile", views.profile, name="profile"),
    path("login", views.signin, name="signin"),
    path("cadastro", views.signup, name="signup"),
    path("billing", views.billing, name="billing"),

]
