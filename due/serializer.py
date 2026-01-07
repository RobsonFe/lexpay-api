from rest_framework import serializers
from .models import DueDiligence, AnaliseDocumento
from oficio.serializer import UserLightSerializer, PrecatorioSerializer


class DueDiligenceSerializer(serializers.ModelSerializer):
    precatorio_detalhes = PrecatorioSerializer(source='precatorio', read_only=True)

    user_detalhes = UserLightSerializer(source='analista', read_only=True)

    class Meta:
        model = DueDiligence
        fields = [
            'id',
            'precatorio',
            'precatorio_detalhes',
            'analista',
            'status_analise',
            'data_inicio_analise',
            'data_conclusao_analise',
            'observacoes',
            'documento_aprovado',
            'motivo_repactuacao',
            'created_at',
            'updated_at',
            'user_detalhes'
        ]

        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'data_conclusao_analise',
            'data_inicio_analise',
            'analista'
        ]

    def validate(self, data):
        dados_instance = {}
        if self.instance:
            dados_instance = {
                'status_analise': self.instance.status_analise,
                'observacoes': self.instance.observacoes,
                'motivo_repactuacao': self.instance.motivo_repactuacao,
                'documento_aprovado': self.instance.documento_aprovado,
            }
        
        dados = {**dados_instance, **data}

        status_analise = dados.get('status_analise')
        documento_aprovado = dados.get('documento_aprovado')
        observacoes = dados.get('observacoes')
        motivo_repactuacao = dados.get('motivo_repactuacao')

        if status_analise == DueDiligence.StatusAnalise.REJEITADO and not observacoes:
            raise serializers.ValidationError({'observacoes': 'O campo de observações tem que ser preenchido'})
        
        if status_analise == DueDiligence.StatusAnalise.REPACTUADO:
            if not motivo_repactuacao:
                raise serializers.ValidationError({'motivo_repactuacao': 'Informar o motivo.'})
            if not observacoes:
                raise serializers.ValidationError({'observacoes': 'Preencher o campo de observações.'})
            
        if status_analise == DueDiligence.StatusAnalise.APROVADO:
            
            if not documento_aprovado:
                raise serializers.ValidationError({'documento_aprovado': 'Verifique a aprovação do documento.'})

            if self.instance:
                pendencias = self.instance.analise_documentos.exclude(
                    status=AnaliseDocumento.StatusDocumento.APROVADO
                ).exists()

                if pendencias:
                    raise serializers.ValidationError(
                        'Não é possível aprovar pois existem itens pendentes ou rejeitados.'
                    )
        
        return data