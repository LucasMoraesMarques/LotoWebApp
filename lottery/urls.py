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
    path("resultados", views.results_reports, name="results"),
    path("resultados/<int:result_id>", views.results_reports_detail, name="result-detail"),
    path("resultados/<int:result_id>/exportar-jogos", views.export_results_reports_games, name="export-results-reports-games"),
    path("resultados/<int:result_id>/criar-conjunto", views.create_game_set_from_result, name="create_game_set_from_result"),
    path("deletar-resultados/<int:result_id>", views.delete_results_reports, name="delete-results-reports"),
    path("enviar-resultados/<int:result_id>", views.send_results_reports, name="send-results-reports"),
    path("exportar-resultados", views.export_results_reports, name="export-results-reports"),
    path("profile", views.profile, name="profile"),
    path("login", views.CustomLoginView.as_view(), name="login"),
    path("logout", views.CustomLogoutView.as_view(), name="logout"),
    path("cadastro", views.register, name="register"),
    path("billing", views.billing, name="billing"),
    path("get-draws/<str:name>", views.get_draws_numbers, name="get-draws"),
    path("create-results-report", views.create_results_report, name="create-results-report"),
    path("get-combinations", views.get_combinations, name="get-combinations"),
    path("save-games-batch", views.save_games_batch, name="save-games-batch")

]
