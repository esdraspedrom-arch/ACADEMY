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

    def test_inicio_associa_imagens_estaticas_as_modalidades_conhecidas(self):
        Modalidade.objects.create(nome="Muay Thai", ativa=True)
        Modalidade.objects.create(nome="Musculação", ativa=True)

        response = self.client.get(reverse("AMOVE:inicio"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AMOVE/images/muay-thai.jpg")
        self.assertContains(response, "AMOVE/images/musculacao.jpg")
        self.assertContains(response, "Atleta treinando Muay Thai")
        self.assertContains(response, "Atleta treinando com pesos")
