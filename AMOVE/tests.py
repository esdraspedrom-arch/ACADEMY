from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client, TestCase
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

    def test_dashboard_exibe_cards_permitidos_e_atividade_nativa(self):
        Modalidade.objects.create(nome="Yoga")

        painel_vazio = self.client.get(reverse("admin:index"))
        self.assertEqual(painel_vazio.status_code, 200)
        self.assertTemplateUsed(painel_vazio, "admin/index.html")
        self.assertContains(painel_vazio, "/static/AMOVE/css/admin.css")
        self.assertContains(painel_vazio, "/static/AMOVE/images/logo-amove.png")
        self.assertContains(painel_vazio, "Painel administrativo")
        self.assertContains(
            painel_vazio,
            "Gerencie as modalidades, organize as turmas e mantenha as informações da academia atualizadas.",
        )
        self.assertContains(painel_vazio, "Gerenciar modalidades")
        self.assertContains(painel_vazio, reverse("admin:AMOVE_modalidade_changelist"))
        self.assertContains(painel_vazio, "Gerenciar turmas")
        self.assertContains(painel_vazio, reverse("admin:AMOVE_turma_changelist"))
        self.assertContains(painel_vazio, "Gerenciar usuários")
        self.assertContains(painel_vazio, "Gerenciar grupos")
        self.assertContains(painel_vazio, "Nenhuma atividade recente para exibir.")
        self.assertNotContains(painel_vazio, "app-list")

        criacao = self.client.post(
            reverse("admin:AMOVE_modalidade_add"),
            {"nome": "Pilates recente", "descricao": "", "ativa": "on"},
        )
        self.assertEqual(criacao.status_code, 302)

        painel_com_atividade = self.client.get(reverse("admin:index"))
        self.assertContains(painel_com_atividade, "Atividade recente")
        self.assertContains(painel_com_atividade, "Adicionado")
        self.assertContains(painel_com_atividade, "Modalidade")
        self.assertContains(painel_com_atividade, "Pilates recente")
        self.assertContains(
            painel_com_atividade,
            reverse(
                "admin:AMOVE_modalidade_change",
                args=[Modalidade.objects.get(nome="Pilates recente").pk],
            ),
        )

    def test_dashboard_nao_exibe_acoes_sem_permissao_do_modelo(self):
        operador = get_user_model().objects.create_user(
            username="operador-sem-permissoes",
            password="senha-teste",
            is_staff=True,
        )
        self.client.force_login(operador)

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Gerenciar modalidades")
        self.assertNotContains(response, "Cadastrar modalidade")
        self.assertNotContains(response, "Gerenciar turmas")
        self.assertNotContains(response, "Cadastrar turma")
        self.assertNotContains(response, "Gerenciar usuários")
        self.assertNotContains(response, "Gerenciar grupos")

        operador.user_permissions.add(
            Permission.objects.get(
                content_type__app_label="AMOVE",
                codename="view_modalidade",
            ),
            Permission.objects.get(
                content_type__app_label="AMOVE",
                codename="add_modalidade",
            ),
        )
        response_com_permissao = self.client.get(reverse("admin:index"))

        self.assertContains(response_com_permissao, "Gerenciar modalidades")
        self.assertContains(response_com_permissao, "Cadastrar modalidade")
        self.assertNotContains(response_com_permissao, "Gerenciar turmas")
        self.assertNotContains(response_com_permissao, "Cadastrar turma")

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


class CadastroViewsTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.administrador = user_model.objects.create_user(
            username="cadastro-admin",
            password="senha-teste",
            is_staff=True,
        )
        self.usuario_comum = user_model.objects.create_user(
            username="cadastro-comum",
            password="senha-teste",
            is_staff=False,
        )

    def test_menu_exibe_cadastro_e_sair_somente_para_usuario_staff(self):
        inicio_url = reverse("AMOVE:inicio")

        visitante = self.client.get(inicio_url)
        self.assertNotContains(visitante, ">Cadastro</a>", html=False)
        self.assertNotContains(visitante, ">Sair</button>", html=False)

        self.client.force_login(self.usuario_comum)
        usuario_comum = self.client.get(inicio_url)
        self.assertNotContains(usuario_comum, ">Cadastro</a>", html=False)
        self.assertNotContains(usuario_comum, ">Sair</button>", html=False)

        self.client.force_login(self.administrador)
        administrador = self.client.get(inicio_url)
        self.assertContains(
            administrador,
            f'href="{reverse("AMOVE:cadastro")}"',
        )
        self.assertContains(
            administrador,
            f'action="{reverse("admin:logout")}"',
        )
        self.assertContains(administrador, 'name="csrfmiddlewaretoken"')

    def test_visitante_e_redirecionado_para_login_e_nao_pode_cadastrar(self):
        response = self.client.get(reverse("AMOVE:cadastro"))
        post = self.client.post(
            reverse("AMOVE:cadastrar_modalidade"),
            {"nome": "Modalidade não autorizada", "ativa": "on"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("admin:login"), response.url)
        self.assertEqual(post.status_code, 302)
        self.assertIn(reverse("admin:login"), post.url)
        self.assertFalse(
            Modalidade.objects.filter(nome="Modalidade não autorizada").exists()
        )

    def test_usuario_comum_recebe_403_na_pagina_e_nos_posts(self):
        self.client.force_login(self.usuario_comum)

        pagina = self.client.get(reverse("AMOVE:cadastro"))
        modalidade = self.client.post(
            reverse("AMOVE:cadastrar_modalidade"),
            {"nome": "Modalidade bloqueada", "ativa": "on"},
        )
        turma = self.client.post(
            reverse("AMOVE:cadastrar_turma"),
            {
                "modalidade": "",
                "dia_semana": "segunda",
                "horario": "18:00",
                "instrutor": "Pessoa não autorizada",
                "vagas": 10,
            },
        )

        self.assertEqual(pagina.status_code, 403)
        self.assertEqual(modalidade.status_code, 403)
        self.assertEqual(turma.status_code, 403)
        self.assertFalse(Modalidade.objects.filter(nome="Modalidade bloqueada").exists())
        self.assertFalse(Turma.objects.filter(instrutor="Pessoa não autorizada").exists())

    def test_administrador_cadastra_modalidade_e_duplicidade_e_validada(self):
        self.client.force_login(self.administrador)
        formulario = self.client.get(reverse("AMOVE:cadastro"))
        self.assertEqual(formulario.status_code, 200)
        self.assertContains(formulario, "Cadastrar modalidade")
        self.assertContains(formulario, "Cadastrar turma")

        criada = self.client.post(
            reverse("AMOVE:cadastrar_modalidade"),
            {
                "nome": "Boxe",
                "descricao": "Treino de boxe.",
                "ativa": "on",
            },
        )

        self.assertEqual(criada.status_code, 302)
        modalidade = Modalidade.objects.get(nome="Boxe")
        self.assertTrue(modalidade.ativa)
        confirmacao = self.client.get(reverse("AMOVE:cadastro"))
        self.assertEqual(
            list(confirmacao.context["messages"])[0].message,
            'A modalidade "Boxe" foi cadastrada com sucesso.',
        )

        duplicada = self.client.post(
            reverse("AMOVE:cadastrar_modalidade"),
            {"nome": "Boxe", "descricao": "", "ativa": "on"},
        )

        self.assertEqual(duplicada.status_code, 200)
        self.assertContains(duplicada, "Já existe uma modalidade com este nome.")
        self.assertEqual(Modalidade.objects.filter(nome="Boxe").count(), 1)

    def test_modalidade_inativa_nao_aparece_publicamente(self):
        self.client.force_login(self.administrador)
        response = self.client.post(
            reverse("AMOVE:cadastrar_modalidade"),
            {"nome": "Atividade reservada", "descricao": "", "ativa": ""},
        )

        self.assertEqual(response.status_code, 302)
        modalidade = Modalidade.objects.get(nome="Atividade reservada")
        self.assertFalse(modalidade.ativa)
        inicio = self.client.get(reverse("AMOVE:inicio"))
        self.assertNotContains(inicio, "Atividade reservada")

    def test_administrador_cadastra_turma_e_a_grade_mantem_filtros(self):
        modalidade = Modalidade.objects.create(nome="Boxe")
        self.client.force_login(self.administrador)

        response = self.client.post(
            reverse("AMOVE:cadastrar_turma"),
            {
                "modalidade": modalidade.pk,
                "dia_semana": "quarta",
                "horario": "18:30",
                "instrutor": "Joana Instrutora",
                "vagas": 12,
            },
        )

        self.assertEqual(response.status_code, 302)
        turma = Turma.objects.get(instrutor="Joana Instrutora")
        self.assertEqual(turma.horario.strftime("%H:%M"), "18:30")
        self.assertEqual(turma.vagas, 12)
        self.assertContains(
            self.client.get(reverse("AMOVE:cadastro")),
            "A turma de Boxe foi cadastrada",
        )

        grade = self.client.get(
            reverse("AMOVE:lista_turmas"),
            {
                "modalidade": modalidade.pk,
                "dia": "quarta",
                "instrutor": "joana",
            },
        )

        self.assertEqual(list(grade.context["turmas"]), [turma])
        self.assertContains(grade, "18:30")

    def test_erros_de_horario_e_vagas_sao_mostrados_e_nao_criam_turma(self):
        modalidade = Modalidade.objects.create(nome="Funcional")
        self.client.force_login(self.administrador)

        resposta_horario = self.client.post(
            reverse("AMOVE:cadastrar_turma"),
            {
                "modalidade": modalidade.pk,
                "dia_semana": "segunda",
                "horario": "25:90",
                "instrutor": "Instrutor",
                "vagas": 5,
            },
        )
        resposta_vagas = self.client.post(
            reverse("AMOVE:cadastrar_turma"),
            {
                "modalidade": modalidade.pk,
                "dia_semana": "segunda",
                "horario": "18:00",
                "instrutor": "Instrutor",
                "vagas": -1,
            },
        )

        self.assertEqual(resposta_horario.status_code, 200)
        self.assertContains(
            resposta_horario,
            "Informe um horário válido no formato de 24 horas (HH:MM).",
        )
        self.assertEqual(resposta_vagas.status_code, 200)
        self.assertContains(
            resposta_vagas,
            "A quantidade de vagas não pode ser negativa.",
        )
        self.assertEqual(Turma.objects.count(), 0)

    def test_post_de_cadastro_exige_csrf(self):
        cliente_com_csrf = Client(enforce_csrf_checks=True)
        cliente_com_csrf.force_login(self.administrador)
        pagina = cliente_com_csrf.get(reverse("AMOVE:cadastro"))

        self.assertEqual(pagina.status_code, 200)
        bloqueada = cliente_com_csrf.post(
            reverse("AMOVE:cadastrar_modalidade"),
            {"nome": "Sem token", "ativa": "on"},
        )
        self.assertEqual(bloqueada.status_code, 403)
        self.assertFalse(Modalidade.objects.filter(nome="Sem token").exists())

        csrf_token = cliente_com_csrf.cookies["csrftoken"].value
        autorizada = cliente_com_csrf.post(
            reverse("AMOVE:cadastrar_modalidade"),
            {
                "csrfmiddlewaretoken": csrf_token,
                "nome": "Com token CSRF",
                "ativa": "on",
            },
        )

        self.assertEqual(autorizada.status_code, 302)
        self.assertTrue(Modalidade.objects.filter(nome="Com token CSRF").exists())
