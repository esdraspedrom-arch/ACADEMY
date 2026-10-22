
from django.contrib import admin
from .models import Modalidade, Turma


@admin.register(Modalidade)
class ModalidadeAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativa")
    list_filter = ("ativa",)
    search_fields = ("nome",)


@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = (
        "modalidade",
        "dia_semana",
        "horario",
        "instrutor",
        "vagas",
    )
    list_filter = ("modalidade", "dia_semana")
    search_fields = ("instrutor",)
    list_select_related = ("modalidade",)
    ordering = ("dia_semana", "horario")


