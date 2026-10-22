
from django.contrib import admin
from .models import Modalidade, Turma


admin.site.site_header = "AMOVE | Academia Corpo em Movimento"
admin.site.site_title = "Administração AMOVE"
admin.site.index_title = "Painel administrativo"


class SituacaoModalidadeFilter(admin.SimpleListFilter):
    title = "Situação"
    parameter_name = "situacao"

    def lookups(self, request, model_admin):
        return (
            ("ativa", "Ativa"),
            ("inativa", "Inativa"),
        )

    def queryset(self, request, queryset):
        if self.value() == "ativa":
            return queryset.filter(ativa=True)
        if self.value() == "inativa":
            return queryset.filter(ativa=False)
        return queryset


@admin.register(Modalidade)
class ModalidadeAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativa")
    list_filter = (SituacaoModalidadeFilter,)
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
