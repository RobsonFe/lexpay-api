from rest_framework import serializers

from due.models import DueDiligence
from oficio.models import StatusPrecatorioChoices
from oficio.serializer import PrecatorioSerializer
from proposal.models import Proposal, ProposalHistory


class ProposalSerializer(serializers.ModelSerializer):
    valor_liquido_cedente = serializers.DecimalField(
        max_digits=18, decimal_places=2, read_only=True
    )
    valor_liquido_proponente = serializers.DecimalField(
        max_digits=18, decimal_places=2, read_only=True
    )
    lucro = serializers.DecimalField(
        max_digits=18,
        decimal_places=2,
        read_only=True,
        source="margem_lucro_percentual",
    )
    proponente_nome = serializers.ReadOnlyField(source="proponente.username")
    precatorio_detalhes = PrecatorioSerializer(source="precatorio", read_only=True)

    class Meta:
        model = Proposal
        fields = [
            "id",
            "precatorio",
            "precatorio_detalhes",
            "proponente_nome",
            "valor_proposto",
            "taxa_desconto",
            "taxa_juros_anual",
            "prazo_pagamento_meses",
            "data_vencimento",
            "observacoes",
            "valor_liquido_cedente",
            "valor_liquido_proponente",
            "lucro",
            "status",
            "created_at",
        ]
        read_only_fields = ["status", "created_at"]

    def validate(self, data):
        precatorio = data.get("precatorio") or (
            self.instance.precatorio if self.instance else None
        )
        valor_proposto = data.get("valor_proposto")

        if precatorio.status != StatusPrecatorioChoices.DISPONIVEL:
            raise serializers.ValidationError(
                f"O precatório deve estar com status '{StatusPrecatorioChoices.DISPONIVEL}'."
            )

        diligencia_aprovada = DueDiligence.objects.filter(
            precatorio=precatorio, status_analise=DueDiligence.StatusAnalise.APROVADO
        ).exists()

        if not diligencia_aprovada:
            raise serializers.ValidationError(
                "Este precatório não possui uma Due Diligence APROVADA."
            )

        if valor_proposto > precatorio.valor_principal:
            raise serializers.ValidationError(
                {
                    "valor_proposto": "O valor não pode ser superior ao valor principal do precatório."
                }
            )

        return data


class ProposalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalHistory
        fields = (
            "id",
            "proposal",
            "status_anterior",
            "status_novo",
            "valor_anterior",
            "valor_novo",
            "alterado_por",
            "motivo_alteracao",
            "created_at",
        )
        read_only_fields = ("id", "created_at")
