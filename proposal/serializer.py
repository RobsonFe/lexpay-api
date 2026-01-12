
from rest_framework import serializers
from proposal.models import Proposal, ProposalHistory
from oficio.models import StatusPrecatorioChoices
from due.models import DueDiligence


class ProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = 'id', 'status', 'valor_proposto', 'taxa_desconto', 'taxa_juros_anual', 'prazo_pagamento_meses', 'valor_liquido_cedente', 'valor_liquido_proponente', 'data_vencimento', 'margem_lucro_percentual', 'precatorio', 'proponente'
        read_only_fields = ('id', 'created_at', 'updated_at','valor_liquido_cedente', 'valor_liquido_proponente', 'margem_lucro_percentual')

    def create(self, validated_data):
        # Validações específicas para criação
        precatorio = validated_data.get('precatorio')
        diligencia_aprovada = DueDiligence.objects.filter(
            precatorio=precatorio, 
            status_analise='APROVADO' 
        ).exists()

        if precatorio.status != StatusPrecatorioChoices.DISPONIVEL or not diligencia_aprovada:
            raise serializers.ValidationError("O precatório não está disponível ou não possui Due Diligence aprovada.")

        valor_proposto = validated_data.get('valor_proposto', 0)
        taxa_desconto = validated_data.get('taxa_desconto', 0)
        taxa_juros_anual = validated_data.get('taxa_juros_anual', 0)
        prazo_pagamento_meses = validated_data.get('prazo_pagamento_meses', 0)

        if valor_proposto <= 0:
            raise serializers.ValidationError("O valor proposto deve ser maior que zero.")
        if taxa_desconto < 0 or taxa_desconto > 100:
            raise serializers.ValidationError("A taxa de desconto deve estar entre 0 e 100.")
        if taxa_juros_anual < 0 or taxa_juros_anual > 100:
            raise serializers.ValidationError("A taxa de juros anual deve estar entre 0 e 100.")
        if prazo_pagamento_meses <= 0:
            raise serializers.ValidationError("O prazo de pagamento em meses deve ser maior que zero.")
        if taxa_desconto + taxa_juros_anual > 100:
            raise serializers.ValidationError("A soma das taxas de desconto e juros anual deve ser menor ou igual a 100.")

        return super().create(validated_data)

class ProposalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalHistory
        fields = 'id', 'proposal', 'status_anterior', 'status_novo', 'valor_anterior', 'valor_novo', 'alterado_por', 'motivo_alteracao', 'created_at'
        read_only_fields = ('id', 'created_at')
        