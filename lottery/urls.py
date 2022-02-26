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
import django.contrib.auth.views as authViews
app_name = "lottery"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("loterias/", views.lotteries, name="lotteries"),
    path("loterias/<str:name>/", views.lottery_detail, name="lottery-detail"),
    path("loterias/<str:name>/concursos/<int:number>", views.draw_detail, name="draw-detail"),
    path("jogos", views.games, name="games"),
    path("jogos/conjuntos/<int:game_set_id>", views.game_set_detail, name="game-set-detail"),
    path("jogos/colecoes/<int:collection_id>", views.collection_detail, name="collection-detail"),
    path("jogos/colecoes/criar-colecao", views.create_collection, name="create-collection"),
    path("jogos/geradores", views.games_generators, name="generators"),
    path("resultados", views.results, name="results"),
    path("profile", views.profile, name="profile"),
    path("login", views.CustomLoginView.as_view(), name="login"),
    path("logout", views.CustomLogoutView.as_view(), name="logout"),
    path("cadastro", views.register, name="register"),
    path("billing", views.billing, name="billing"),
    path("get-draw", views.get_selected_draw, name="get-draw"),
    path("get-combinations", views.get_combinations, name="get-combinations"),
    path("save-games-batch", views.save_games_batch, name="save-games-batch")

]
