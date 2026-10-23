from django.urls import path

from . import views

app_name = "AMOVE"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("turmas/", views.lista_turmas, name="lista_turmas"),
    path("cadastro/", views.cadastro, name="cadastro"),
    path(
        "cadastro/modalidade/",
        views.cadastrar_modalidade,
        name="cadastrar_modalidade",
    ),
    path("cadastro/turma/", views.cadastrar_turma, name="cadastrar_turma"),
]
