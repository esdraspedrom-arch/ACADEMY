from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Modalidade, Turma


class PaginasPublicasTests(TestCase):
    def test_inicio_exibe_modalidades_ativas_e_dados_oficiais_de_contato(self):
        ativa = Modalidade.objects.create(
            nome="Pilates",
            descricao="Aulas de Pilates.",
            ativa=True,
        )
        Modalidade.objects.create(nome="Yoga", ativa=False)

        response = self.client.get(reverse("AMOVE:inicio"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Academia Corpo em Movimento")
        self.assertContains(
            response,
            "R. São Roque - Nossa Sra. das Dores, Caruaru - PE, 55010-350",
        )
        self.assertContains(response, "(81) 98888-7777")
        self.assertContains(response, 'href="tel:+5581988887777"')
        self.assertContains(
            response,
            "https://www.google.com/maps/search/?api=1&amp;query="
            "R.%20S%C3%A3o%20Roque%20-%20Nossa%20Sra.%20das%20Dores%2C%20"
            "Caruaru%20-%20PE%2C%2055010-350",
        )
        self.assertContains(response, ativa.nome)
        self.assertContains(response, ativa.descricao)
        self.assertContains(response, 'role="img"')
        self.assertContains(response, "Imagem em preparação")
        self.assertNotContains(response, "Yoga")

    def test_turmas_sao_ordenadas_por_dia_e_horario(self):
        modalidade = Modalidade.objects.create(nome="Pilates")
        turmas = [
            Turma.objects.create(
                modalidade=modalidade,
                dia_semana="sabado",
                horario="09:00",
                instrutor="Ana",
                vagas=10,
            ),
            Turma.objects.create(
                modalidade=modalidade,
                dia_semana="segunda",
                horario="18:00",
                instrutor="Bruna",
                vagas=8,
            ),
            Turma.objects.create(
                modalidade=modalidade,
                dia_semana="segunda",
                horario="09:00",
                instrutor="Carlos",
                vagas=12,
            ),
            Turma.objects.create(
                modalidade=modalidade,
                dia_semana="terca",
                horario="10:00",
                instrutor="Daniela",
                vagas=9,
            ),
        ]

        response = self.client.get(reverse("AMOVE:lista_turmas"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["turmas"]),
            [turmas[2], turmas[1], turmas[3], turmas[0]],
        )
        self.assertContains(response, modalidade.nome)
        self.assertContains(response, "Segunda")
        self.assertContains(response, "Bruna")

    def test_filtro_de_modalidade_e_mantido_no_formulario(self):
        selecionada = Modalidade.objects.create(nome="Muay Thai")
        outra = Modalidade.objects.create(nome="Funcional")
        turma_selecionada = Turma.objects.create(
            modalidade=selecionada,
            dia_semana="segunda",
            horario="18:00",
            instrutor="Ana",
        )
        Turma.objects.create(
            modalidade=outra,
            dia_semana="segunda",
            horario="19:00",
            instrutor="Bruna",
        )

        response = self.client.get(
            reverse("AMOVE:lista_turmas"),
            {"modalidade": selecionada.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["turmas"]), [turma_selecionada])
        self.assertEqual(
            response.context["filtros"]["modalidade"],
            str(selecionada.pk),
        )

    def test_filtros_de_dia_e_busca_parcial_por_instrutor(self):
        modalidade = Modalidade.objects.create(nome="Funcional")
        correspondente = Turma.objects.create(
            modalidade=modalidade,
            dia_semana="terca",
            horario="18:00",
            instrutor="Ana Paula",
        )
        Turma.objects.create(
            modalidade=modalidade,
            dia_semana="terca",
            horario="19:00",
            instrutor="Bruna",
        )
        Turma.objects.create(
            modalidade=modalidade,
            dia_semana="quarta",
            horario="18:00",
            instrutor="Ana Paula",
        )

        resposta_dia = self.client.get(
            reverse("AMOVE:lista_turmas"),
            {"dia": "terca"},
        )
        resposta_instrutor = self.client.get(
            reverse("AMOVE:lista_turmas"),
            {"instrutor": "paul"},
        )
        resposta_combinada = self.client.get(
            reverse("AMOVE:lista_turmas"),
            {
                "modalidade": modalidade.pk,
                "dia": "terca",
                "instrutor": "paul",
            },
        )

        self.assertEqual(list(resposta_dia.context["turmas"]), [
            turma
            for turma in Turma.objects.filter(dia_semana="terca").order_by("horario")
        ])
        self.assertEqual(
            list(resposta_instrutor.context["turmas"]),
            [correspondente, Turma.objects.get(dia_semana="quarta")],
        )
        self.assertEqual(list(resposta_combinada.context["turmas"]), [correspondente])
        self.assertContains(resposta_combinada, 'value="terca" selected')
        self.assertContains(resposta_combinada, 'value="paul"')

    def test_filtro_sem_resultados_mostra_mensagem_amigavel(self):
        modalidade = Modalidade.objects.create(nome="Sem turmas")

        response = self.client.get(
            reverse("AMOVE:lista_turmas"),
            {"modalidade": modalidade.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Nenhuma turma encontrada com os filtros selecionados.",
        )

    def test_limpar_filtros_retorna_a_rota_sem_parametros_get(self):
        response = self.client.get(reverse("AMOVE:lista_turmas"))

        self.assertContains(
            response,
            f'href="{reverse("AMOVE:lista_turmas")}"',
        )

    def test_card_da_modalidade_abre_grade_filtrada_por_id(self):
        modalidade = Modalidade.objects.create(nome="Muay Thai", ativa=True)
        outra = Modalidade.objects.create(nome="Funcional", ativa=True)
        turma = Turma.objects.create(
            modalidade=modalidade,
            dia_semana="sabado",
            horario="09:00",
            instrutor="Carlos",
        )
        Turma.objects.create(
            modalidade=outra,
            dia_semana="segunda",
            horario="08:00",
            instrutor="Bruna",
        )

        inicio = self.client.get(reverse("AMOVE:inicio"))
        grade = self.client.get(
            reverse("AMOVE:lista_turmas"),
            {"modalidade": modalidade.pk},
        )

        self.assertContains(
            inicio,
            f'href="{reverse("AMOVE:lista_turmas")}?modalidade={modalidade.pk}"',
        )
        self.assertContains(
            inicio,
            f'aria-label="Ver turmas de {modalidade.nome}"',
        )
        self.assertEqual(list(grade.context["turmas"]), [turma])
        self.assertContains(grade, "Sábado")

    def test_modalidade_sem_turmas_nao_mostra_turmas_de_outras(self):
        sem_turmas = Modalidade.objects.create(nome="Pilates")
        outra = Modalidade.objects.create(nome="Musculação")
        Turma.objects.create(
            modalidade=outra,
            dia_semana="segunda",
            horario="08:00",
            instrutor="Bruna",
        )

        response = self.client.get(
            reverse("AMOVE:lista_turmas"),
            {"modalidade": sem_turmas.pk},
        )

        self.assertEqual(list(response.context["turmas"]), [])
        self.assertNotContains(
            response,
            'data-label="Modalidade">Musculação',
            html=False,
        )
        self.assertContains(response, "Nenhuma turma encontrada")

    def test_inicio_associa_imagens_estaticas_as_modalidades_conhecidas(self):
        Modalidade.objects.create(nome="Muay Thai", ativa=True)
        Modalidade.objects.create(nome="Musculação", ativa=True)

        response = self.client.get(reverse("AMOVE:inicio"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AMOVE/images/muay-thai.jpg")
        self.assertContains(response, "AMOVE/images/musculacao.jpg")
        self.assertContains(response, "Atleta treinando Muay Thai")
        self.assertContains(response, "Atleta treinando com pesos")


class AdminModalidadesTests(TestCase):
    def test_lista_de_modalidades_pode_ser_filtrada_por_situacao(self):
        Modalidade.objects.create(nome="Funcional ativa", ativa=True)
        Modalidade.objects.create(nome="Pilates inativa", ativa=False)
        usuario = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="senha-teste",
        )
        self.client.force_login(usuario)
        url = reverse("admin:AMOVE_modalidade_changelist")

        ativas = self.client.get(url, {"situacao": "ativa"})
        inativas = self.client.get(url, {"situacao": "inativa"})

        self.assertEqual(ativas.status_code, 200)
        self.assertEqual(
            list(ativas.context["cl"].queryset.values_list("nome", flat=True)),
            ["Funcional ativa"],
        )
        self.assertEqual(
            list(inativas.context["cl"].queryset.values_list("nome", flat=True)),
            ["Pilates inativa"],
        )
        self.assertContains(ativas, "Ativa")
        self.assertContains(ativas, "Inativa")


class AdminInterfaceTests(TestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            username="admin-interface",
            email="admin-interface@example.com",
            password="senha-teste",
        )
        self.client.force_login(self.admin)

    def test_login_e_painel_carregam_identidade_visual_amove(self):
        self.client.logout()
        login = self.client.get(reverse("admin:login"))

        self.assertEqual(login.status_code, 200)
        self.assertContains(login, "/static/AMOVE/css/admin.css")
        self.assertContains(login, "/static/AMOVE/images/logo-amove.png")
        self.assertContains(login, 'name="csrfmiddlewaretoken"')

        falha_login = self.client.post(
            reverse("admin:login"),
            {"username": self.admin.username, "password": "senha-incorreta"},
        )
        self.assertEqual(falha_login.status_code, 200)
        self.assertContains(falha_login, "errornote")

        login_valido = self.client.post(
            reverse("admin:login"),
            {
                "username": self.admin.username,
                "password": "senha-teste",
                "next": reverse("admin:index"),
            },
        )
        self.assertEqual(login_valido.status_code, 302)
        self.assertTrue(self.client.session.get("_auth_user_id"))
        painel = self.client.get(reverse("admin:index"))

        self.assertEqual(painel.status_code, 200)
        self.assertContains(painel, "AMOVE | Academia Corpo em Movimento")
        self.assertContains(painel, "Modalidades")
        self.assertContains(painel, "Turmas")
        self.assertContains(painel, "/static/AMOVE/css/admin.css")

        publico = self.client.get(reverse("AMOVE:inicio"))
        self.assertEqual(publico.status_code, 200)
        self.assertContains(publico, "/static/AMOVE/css/style.css")
        self.assertNotContains(publico, "/static/AMOVE/css/admin.css")

    def test_modalidade_pode_ser_criada_editada_e_excluida_no_admin(self):
        adicionar_url = reverse("admin:AMOVE_modalidade_add")
        criada = self.client.post(
            adicionar_url,
            {"nome": "Pilates Admin", "descricao": "Descrição inicial", "ativa": "on"},
        )

        self.assertEqual(criada.status_code, 302)
        modalidade = Modalidade.objects.get(nome="Pilates Admin")
        editar = self.client.post(
            reverse("admin:AMOVE_modalidade_change", args=[modalidade.pk]),
            {
                "nome": "Pilates Atualizado",
                "descricao": "Descrição revisada",
                "ativa": "on",
            },
        )
        modalidade.refresh_from_db()
        self.assertEqual(editar.status_code, 302)
        self.assertEqual(modalidade.nome, "Pilates Atualizado")

        confirmacao = self.client.get(
            reverse("admin:AMOVE_modalidade_delete", args=[modalidade.pk])
        )
        exclusao = self.client.post(
            reverse("admin:AMOVE_modalidade_delete", args=[modalidade.pk]),
            {"post": "yes"},
        )

        self.assertEqual(confirmacao.status_code, 200)
        self.assertContains(confirmacao, "Are you sure")
        self.assertEqual(exclusao.status_code, 302)
        self.assertFalse(Modalidade.objects.filter(pk=modalidade.pk).exists())

    def test_turma_pode_ser_criada_editada_pesquisada_e_filtrada_no_admin(self):
        modalidade = Modalidade.objects.create(nome="Funcional admin")
        adicionar_url = reverse("admin:AMOVE_turma_add")
        criada = self.client.post(
            adicionar_url,
            {
                "modalidade": modalidade.pk,
                "dia_semana": "segunda",
                "horario": "18:00",
                "instrutor": "Ana Admin",
                "vagas": 10,
            },
        )

        self.assertEqual(criada.status_code, 302)
        turma = Turma.objects.get(instrutor="Ana Admin")
        editar = self.client.post(
            reverse("admin:AMOVE_turma_change", args=[turma.pk]),
            {
                "modalidade": modalidade.pk,
                "dia_semana": "terca",
                "horario": "19:00",
                "instrutor": "Ana Atualizada",
                "vagas": 8,
            },
        )
        turma.refresh_from_db()
        self.assertEqual(editar.status_code, 302)
        self.assertEqual(turma.instrutor, "Ana Atualizada")

        lista = self.client.get(
            reverse("admin:AMOVE_turma_changelist"),
            {"q": "Atualizada", "dia_semana__exact": "terca"},
        )

        self.assertEqual(lista.status_code, 200)
        self.assertEqual(
            list(lista.context["cl"].queryset),
            [turma],
        )
