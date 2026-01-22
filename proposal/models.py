import uuid
from decimal import Decimal

from django.db import models
from django.db.models import  DecimalField, ExpressionWrapper, F, Value

from auth.models import User
from due.models import DueDiligence
from oficio.models import Precatorio


class ProposalQuerySet(models.QuerySet):
    def com_score_atratividade(self):
        return (
            self.filter(precatorio__status="Disponível")
            .annotate(
                margem_db=ExpressionWrapper(
                    (F("precatorio__valor_principal") - F("valor_proposto"))
                    / F("valor_proposto")
                    * Value(100),
                    output_field=DecimalField(),
                )
            )
            .annotate(
                score=ExpressionWrapper(
                    (F("margem_db") * Value(0.4))
                    + ((Value(100) - F("taxa_desconto")) * Value(0.3))
                    + ((Value(120) - F("prazo_pagamento_meses")) * Value(0.2)),
                    output_field=DecimalField(),
                )
            )
            .order_by("-score")
        )


class StausChoices:

    RASCUNHO = "Rascunho"
    ENVIADA = "Enviada"
    ACEITA = "Aceita"
    REJEITADA = "Rejeitada"
    EXPIRADA = "Expirada"

    STATUS = [
        ("RASCUNHO", "rascunho"),
        ("ENVIADA", "enviada"),
        ("ACEITA", "aceita"),
        ("REJEITADA", "rejeitada"),
        ("EXPIRADA", "expirada"),
    ]


class Proposal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    precatorio = models.ForeignKey(
        Precatorio, on_delete=models.PROTECT, blank=False, null=False
    )
    proponente = models.ForeignKey(
        User, on_delete=models.PROTECT, limit_choices_to={"type_user": "Broker"}
    )
    valor_proposto = models.DecimalField(max_digits=18, decimal_places=2)
    taxa_desconto = models.DecimalField(max_digits=5, decimal_places=2)
    taxa_juros_anual = models.DecimalField(max_digits=5, decimal_places=2)
    prazo_pagamento_meses = models.IntegerField()
    valor_liquido_cedente = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    valor_liquido_proponente = models.DecimalField(
        max_digits=18, decimal_places=2, blank=True, null=True
    )
    status = models.CharField(
        max_length=20, choices=StausChoices.STATUS, default="RASCUNHO"
    )
    data_vencimento = models.DateField()
    observacoes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    _current_user = None

    @property
    def margem_lucro_percentual(self):
        if self.valor_proposto > 0:
            valor_face = self.precatorio.valor_principal

            return ((valor_face - self.valor_proposto) / self.valor_proposto) * Decimal(
                "100"
            )

        return 0

    def __str__(self):
        return f"Proposal: {self.id} - {self.status}, Proponente: {self.proponente} Valor: {self.valor_proposto} Vencimento: {self.data_vencimento}"

    def save(self, *args, **kwargs):

        valor_face_precatorio = self.precatorio.valor_principal
        percentual_honorarios_precatorio = self.precatorio.percentual_honorarios

        honorarios = self.valor_proposto * (percentual_honorarios_precatorio / 100)

        self.valor_liquido_cedente = self.valor_proposto - honorarios

        if self.prazo_pagamento_meses > 0:

            base_juros = Decimal("1") + (self.taxa_juros_anual / Decimal("100"))
            fator_tempo = base_juros ** (self.prazo_pagamento_meses / Decimal("12"))
            valor_final = self.valor_proposto * fator_tempo
            custo_juros = valor_final - self.valor_proposto
            self.valor_liquido_proponente = (
                valor_face_precatorio - self.valor_proposto - custo_juros
            )
        else:
            self.valor_liquido_proponente = valor_face_precatorio - self.valor_proposto

        super().save(*args, **kwargs)

    objects = ProposalQuerySet.as_manager()


class ProposalHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    status_anterior = models.CharField(
        max_length=20, choices=StausChoices.STATUS, default="RASCUNHO"
    )
    status_novo = models.CharField(
        max_length=20, choices=StausChoices.STATUS, default="ENVIADA"
    )
    valor_anterior = models.DecimalField(
        max_digits=18, decimal_places=2, null=False, blank=False
    )
    valor_novo = models.DecimalField(
        max_digits=18, decimal_places=2, null=False, blank=False
    )
    alterado_por = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    motivo_alteracao = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ProposalHistory: {self.proposal.id} - {self.status_anterior} -> {self.status_novo} alterado por {self.alterado_por} Pelo motivo: {self.motivo_alteracao}"
