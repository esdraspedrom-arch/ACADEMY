from django import forms

from .models import Modalidade, Turma


class ModalidadeForm(forms.ModelForm):
    class Meta:
        model = Modalidade
        fields = ("nome", "descricao", "ativa")
        labels = {
            "nome": "Nome da modalidade",
            "descricao": "Descrição",
            "ativa": "Modalidade ativa",
        }
        error_messages = {
            "nome": {
                "unique": "Já existe uma modalidade com este nome.",
            },
        }
        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "autocomplete": "off",
                    "placeholder": "Ex.: Funcional",
                }
            ),
            "descricao": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Conte um pouco sobre esta modalidade",
                }
            ),
        }


class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = ("modalidade", "dia_semana", "horario", "instrutor", "vagas")
        labels = {
            "modalidade": "Modalidade",
            "dia_semana": "Dia da semana",
            "horario": "Horário",
            "instrutor": "Instrutor",
            "vagas": "Quantidade de vagas",
        }
        error_messages = {
            "horario": {
                "invalid": "Informe um horário válido no formato de 24 horas (HH:MM).",
            },
            "vagas": {
                "invalid": "Informe uma quantidade válida de vagas.",
                "min_value": "A quantidade de vagas não pode ser negativa.",
            },
        }
        widgets = {
            "modalidade": forms.Select(),
            "dia_semana": forms.Select(),
            "horario": forms.TimeInput(
                format="%H:%M",
                attrs={"type": "time"},
            ),
            "instrutor": forms.TextInput(
                attrs={
                    "autocomplete": "name",
                    "placeholder": "Nome do instrutor",
                }
            ),
            "vagas": forms.NumberInput(attrs={"min": 0}),
        }
