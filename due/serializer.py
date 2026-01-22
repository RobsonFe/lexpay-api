from rest_framework import serializers
from django.utils import timezone
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

            if not self.instance:
                raise serializers.ValidationError('Não é possível criar uma Due Diligence já aprovada.')
            
            pendencias = self.instance.analise_documentos.exclude(
                status=AnaliseDocumento.StatusDocumento.APROVADO
            ).exists()

            if pendencias:
                raise serializers.ValidationError(
                    'Não é possível aprovar pois existem itens pendentes ou rejeitados.'
                )
            data['documento_aprovado'] = True
        
        return data

class DueDiligenceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model= DueDiligence
        fields = ['id', 'precatorio', 'observacoes', 'prioridade', 'analista']
        read_only_fields = ['id','analista']

class AnaliseDocumentoSerializer(serializers.ModelSerializer):
    precatorio_detalhes = PrecatorioSerializer(source='due_diligence.precatorio', read_only=True)
    detalhes_usuario = UserLightSerializer(source='analisado_por', read_only=True)
    due_diligence_detalhes = DueDiligenceSerializer(source='due_diligence', read_only=True)

    class Meta:
        model = AnaliseDocumento
        fields = [
            'id', 
            'status',
            'observacoes_analise',
            'data_analise',
            'documento',             
            'due_diligence',      
            'analisado_por',      
            'due_diligence_detalhes',
            'precatorio_detalhes',
            'detalhes_usuario'
        ]
        read_only_fields = fields

class AnaliseDocumentoUpdateSerializer(serializers.ModelSerializer):
    
    detalhes_usuario = UserLightSerializer(source='analisado_por', read_only=True)
    class Meta:
        model = AnaliseDocumento
        fields = [
            'id', 
            'due_diligence',          
            'documento',       
            'status',
            'observacoes_analise',
            'data_analise',
            'analisado_por',          
            'detalhes_usuario',          
        ]
        read_only_fields = [
            'id', 
            'due_diligence',
            'detalhes_usuario',
            'precatorio_detalhes'
        ]
        
        
    def update(self, instance, validated_data):
        user = self.context['request'].user
        instance.data_analise = timezone.now()
        instance.analisado_por = user
        
        for key, value in validated_data.items():
            setattr(instance, key, value)
        
        instance.save()
        
        return instance
