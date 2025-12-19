from django.db import models
from uuid import uuid4
from oficio.models import Precatorio
from auth.models import User, TypeUserChoices

class DueDiligence(models.Model):

    class StatusAnalise(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        EM_ANALISE = "EM_ANALISE", "Em analise"
        APROVADO = "APROVADO", "Aprovado"
        REPACTUADO = "REPACTUADO", "Repactuado"
        REJEITADO = "REJEITADO", "Rejeitado"

    id = models.UUIDField(default=uuid4, editable=False, primary_key=True, unique=True)
    precatorio = models.ForeignKey(Precatorio, on_delete=models.PROTECT, related_name="diligencias")
    analista = models.ForeignKey(
        User, on_delete=models.PROTECT, limit_choices_to={
            'type_user__in':[
                TypeUserChoices.BROKER,
                TypeUserChoices.ADMINISTRADOR
                ]},related_name="analises_feitas")
    status_analise = models.CharField(max_length=20, choices=StatusAnalise.choices, default=StatusAnalise.PENDENTE, db_index=True)
    data_inicio_analise = models.DateField(null=True, blank=True)
    data_conclusao_analise = models.DateField(null=True, blank=True)
    observacoes = models.TextField(null=False, blank=False)
    motivo_repactuacao = models.TextField(null=True, blank=True)
    documento_aprovado =  models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "due_diligence"
        verbose_name = "Due Diligence"
        verbose_name_plural = "Due Diligences"
        ordering = ['-created_at']

    def __str__(self):
        return f"Analise {self.precatorio.numero_processo} - {self.get_status_analise_display()}"
