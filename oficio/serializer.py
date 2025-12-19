from rest_framework import serializers
from .models import Tribunal, EnteDevedor, Precatorio, Documento
from auth.models import User
from django.conf import settings


class TribunalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tribunal
        fields = ['id', 'nome', 'sigla', 'uf']

class EnteDevedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnteDevedor
        fields = ['id', 'nome', 'cnpj', 'esfera']

class UserLightSerializer(serializers.ModelSerializer):
    """
    Serializer leve apenas para mostrar quem é o Cedente/Advogado
    sem expor dados sensíveis do User.
    """
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'type_user', 'avatar']

    def get_avatar(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return f"{settings.MEDIA_URL}{obj.avatar}"
        return None

class DocumentoSerializer(serializers.ModelSerializer):
    extension = serializers.ReadOnlyField(source='get_file_extension')
    size_mb = serializers.ReadOnlyField(source='get_file_size_mb')
    
    class Meta:
        model = Documento
        fields = ['id', 'precatorio', 'titulo', 'arquivo', 'enviado_em', 'extension', 'size_mb']
        read_only_fields = ['enviado_em', 'extension', 'size_mb']

class PrecatorioSerializer(serializers.ModelSerializer):
    tribunal_id = serializers.PrimaryKeyRelatedField(
        queryset=Tribunal.objects.all(), source='tribunal', write_only=True
    )
    ente_devedor_id = serializers.PrimaryKeyRelatedField(
        queryset=EnteDevedor.objects.all(), source='ente_devedor', write_only=True
    )
    tribunal = TribunalSerializer(read_only=True)
    ente_devedor = EnteDevedorSerializer(read_only=True)
    cedente = UserLightSerializer(read_only=True)
    advogado = UserLightSerializer(read_only=True)
    documentos = DocumentoSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    natureza_display = serializers.CharField(source='get_natureza_display', read_only=True)

    class Meta:
        model = Precatorio
        fields = [
            'id', 
            'numero_processo', 
            'natureza', 'natureza_display',
            'valor_principal', 
            'valor_venda', 
            'percentual_honorarios',
            'data_expedicao', 
            'ano_orcamentario',
            'status', 'status_display',
            'descricao',
            'tribunal','tribunal_id',
            'ente_devedor','ente_devedor_id',
            'cedente',
            'advogado',
            'documentos',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['cedente', 'created_at', 'updated_at']

    def validate(self, data):
        """
        Validações de Regra de Negócio.
        Verifica se o valor de venda não excede o valor principal.
        """
        valor_venda = data.get('valor_venda')
        valor_principal = data.get('valor_principal')
        
        if valor_venda and valor_principal:
            if valor_venda > valor_principal:
                raise serializers.ValidationError({
                    'valor_venda': 'O valor de venda não pode ser maior que o valor principal.'
                })
        
        if self.instance:
            valor_principal = valor_principal or self.instance.valor_principal
            if valor_venda and valor_venda > valor_principal:
                raise serializers.ValidationError({
                    'valor_venda': 'O valor de venda não pode ser maior que o valor principal.'
                })
        
        return data

    def create(self, validated_data):
        """
        Injeta o usuário logado como Cedente automaticamente se não for Admin.
        """
        request = self.context.get('request')
        
        if request and hasattr(request, 'user'):

            validated_data['cedente'] = request.user
            
        return super().create(validated_data)

class PrecatorioUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer específico para atualizações (PATCH/PUT), 
    caso queira restringir campos que não podem ser mudados após criação
    (ex: não mudar o tribunal ou número do processo).
    """
    class Meta:
        model = Precatorio
        fields = ['valor_venda', 'status', 'descricao', 'percentual_honorarios']