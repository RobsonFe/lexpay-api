
'''from rest_framework import serializers
from proposal.models import Proposal, ProposalHistory


class ProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = 'id, status, valor_proposto, taxa_desconto, taxa_juros_anual, prazo_pagamento_meses, valor_liquido_cedente, valor_liquido_proponente, data_vencimento', 'margem_lucro_percentual'
        read_only_fields = ('id', 'created_at', 'update_at')

class ProposalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProposalHistory
        fields = 'id, proposal, status_anterior, status_novo, valor_anterior, valor_novo, alterado_por, motivo_alteracao, created_at'
        read_only_fields = ('id', 'created_at')
        '''