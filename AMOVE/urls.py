from django.urls import path

from . import views

app_name = "AMOVE"

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("turmas/", views.lista_turmas, name="lista_turmas"),
]
