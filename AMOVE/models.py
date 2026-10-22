from django.db import models

class Modalidade(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    ativa = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Modalidade"
        verbose_name_plural = "Modalidades"

    def __str__(self):
        return self.nome


class Turma(models.Model):
    DIAS_DA_SEMANA = [
        ("segunda", "Segunda"),
        ("terca", "Terça"),
        ("quarta", "Quarta"),
        ("quinta", "Quinta"),
        ("sexta", "Sexta"),
        ("sabado", "Sábado"),
    ]

    modalidade = models.ForeignKey(
        Modalidade,
        on_delete=models.PROTECT,
        related_name="turmas",
    )
    dia_semana = models.CharField(
        max_length=10,
        choices=DIAS_DA_SEMANA,
    )
    horario = models.TimeField()
    instrutor = models.CharField(max_length=100)
    vagas = models.PositiveIntegerField(default=10)

    class Meta:
        ordering = ["dia_semana", "horario"]
        verbose_name = "Turma"
        verbose_name_plural = "Turmas"

    def __str__(self):
        return (
            f"{self.modalidade.nome} — "
            f"{self.get_dia_semana_display()} "
            f"{self.horario.strftime('%H:%M')}"
        )

