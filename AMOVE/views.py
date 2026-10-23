from urllib.parse import quote
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles import finders
from django.db.models import Case, IntegerField, Value, When
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from django.utils.text import slugify

from .forms import ModalidadeForm, TurmaForm
from .models import Modalidade, Turma


IMAGENS_MODALIDADES = {
    "muay-thai": ("AMOVE/images/muay-thai.jpg", "Atleta treinando Muay Thai"),
    "musculacao": ("AMOVE/images/musculacao.jpg", "Atleta treinando com pesos"),
}


ACADEMIA = {
    "nome": "Academia Corpo em Movimento",
    "endereco": "R. São Roque - Nossa Sra. das Dores, Caruaru - PE, 55010-350",
    "telefone": "(81) 98888-7777",
    "telefone_link": "tel:+5581988887777",
}


def _is_staff(user):
    return user.is_staff


def staff_required(view_func):
    @wraps(view_func)
    @login_required(login_url="admin:login")
    def wrapped_view(request, *args, **kwargs):
        if not _is_staff(request.user):
            return HttpResponseForbidden("Acesso restrito a administradores.")
        return view_func(request, *args, **kwargs)

    return wrapped_view


def inicio(request):
    modalidades = []
    for modalidade in Modalidade.objects.filter(ativa=True):
        imagem = IMAGENS_MODALIDADES.get(slugify(modalidade.nome))
        imagem_disponivel = imagem and finders.find(imagem[0])
        modalidades.append(
            {
                "modalidade": modalidade,
                "imagem": imagem[0] if imagem_disponivel else None,
                "texto_alternativo": (
                    imagem[1]
                    if imagem_disponivel
                    else f"Imagem de {modalidade.nome} indisponível"
                ),
            }
        )

    academia = {
        **ACADEMIA,
        "mapas_url": (
            "https://www.google.com/maps/search/?api=1&query="
            f"{quote(ACADEMIA['endereco'], safe='')}"
        ),
    }
    return render(
        request,
        "AMOVE/inicio.html",
        {"academia": academia, "modalidades": modalidades},
    )


def lista_turmas(request):
    modalidade_id = request.GET.get("modalidade", "").strip()
    dia_semana = request.GET.get("dia", "").strip()
    instrutor = request.GET.get("instrutor", "").strip()

    ordem_dias = Case(
        When(dia_semana="segunda", then=Value(1)),
        When(dia_semana="terca", then=Value(2)),
        When(dia_semana="quarta", then=Value(3)),
        When(dia_semana="quinta", then=Value(4)),
        When(dia_semana="sexta", then=Value(5)),
        When(dia_semana="sabado", then=Value(6)),
        default=Value(7),
        output_field=IntegerField(),
    )
    turmas = (
        Turma.objects.select_related("modalidade")
        .annotate(_ordem_dia=ordem_dias)
        .order_by("_ordem_dia", "horario")
    )

    if modalidade_id:
        try:
            modalidade_id = int(modalidade_id)
        except ValueError:
            turmas = turmas.none()
        else:
            turmas = turmas.filter(modalidade_id=modalidade_id)

    dias_validos = {valor for valor, _ in Turma.DIAS_DA_SEMANA}
    if dia_semana:
        if dia_semana in dias_validos:
            turmas = turmas.filter(dia_semana=dia_semana)
        else:
            turmas = turmas.none()

    if instrutor:
        turmas = turmas.filter(instrutor__icontains=instrutor)

    return render(
        request,
        "AMOVE/turmas.html",
        {
            "turmas": turmas,
            "modalidades": Modalidade.objects.order_by("nome"),
            "dias_da_semana": Turma.DIAS_DA_SEMANA,
            "filtros": {
                "modalidade": str(modalidade_id) if modalidade_id else "",
                "dia": dia_semana,
                "instrutor": instrutor,
            },
            "filtros_aplicados": bool(modalidade_id or dia_semana or instrutor),
        },
    )


@staff_required
@require_GET
def cadastro(request):
    return render(
        request,
        "AMOVE/cadastro.html",
        {
            "modalidade_form": ModalidadeForm(),
            "turma_form": TurmaForm(),
        },
    )


@staff_required
@require_POST
def cadastrar_modalidade(request):
    form = ModalidadeForm(request.POST)
    if form.is_valid():
        modalidade = form.save()
        messages.success(
            request,
            f'A modalidade "{modalidade.nome}" foi cadastrada com sucesso.',
        )
        return redirect(f"{reverse('AMOVE:cadastro')}#cadastro-modalidade")

    return render(
        request,
        "AMOVE/cadastro.html",
        {
            "modalidade_form": form,
            "turma_form": TurmaForm(),
        },
    )


@staff_required
@require_POST
def cadastrar_turma(request):
    form = TurmaForm(request.POST)
    if form.is_valid():
        turma = form.save()
        messages.success(
            request,
            f"A turma de {turma.modalidade.nome} foi cadastrada com sucesso.",
        )
        return redirect(f"{reverse('AMOVE:cadastro')}#cadastro-turma")

    return render(
        request,
        "AMOVE/cadastro.html",
        {
            "modalidade_form": ModalidadeForm(),
            "turma_form": form,
        },
    )
