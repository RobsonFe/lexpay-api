from rest_framework import serializers
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from auth.models import Address, User


class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer para endereços.
    Permite criar, ler, atualizar e deletar endereços.
    """
    class Meta:
        model = Address
        fields = ('id', 'address', 'number', 'complement', 'city', 'state', 'zip_code', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para CRIAÇÃO de usuário.
    Permite criar usuário junto com endereços em uma única requisição.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    addresses = AddressSerializer(many=True, required=False)
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'password', 'password_confirm', 
            'name', 'cpf', 'phone', 'avatar', 'addresses'
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        """
        Valida se as senhas coincidem.
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password_confirm": "As senhas não coincidem."
            })
        return attrs

    def create(self, validated_data):
        """
        Cria o usuário e seus endereços associados.
        """
        addresses_data = validated_data.pop('addresses', [])
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        for address_data in addresses_data:
            Address.objects.create(user=user, **address_data)
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para ATUALIZAÇÃO de usuário.
    Permite atualizar usuário e seus endereços.
    """
    addresses = AddressSerializer(many=True, required=False)
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'name', 'cpf', 'phone', 
            'avatar', 'is_active', 'is_staff', 'created_at', 
            'updated_at', 'addresses'
        )
        read_only_fields = ('id', 'is_active', 'is_staff', 'created_at', 'updated_at')

    def update(self, instance, validated_data):
        """
        Atualiza o usuário e seus endereços.
        Permite criar novos endereços, atualizar existentes ou deletar endereços.
        """
        addresses_data = validated_data.pop('addresses', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if addresses_data is not None:
            existing_address_ids = set()
            
            for address_data in addresses_data:
                address_id = address_data.pop('id', None)
                
                if address_id:
                    try:
                        address = Address.objects.get(id=address_id, user=instance)
                        for attr, value in address_data.items():
                            setattr(address, attr, value)
                        address.save()
                        existing_address_ids.add(address_id)
                    except Address.DoesNotExist:
                        Address.objects.create(user=instance, **address_data)
                else:
                    Address.objects.create(user=instance, **address_data)
        
        return instance


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer para LEITURA de usuário.
    Retorna usuário com todos os endereços associados.
    """
    addresses = AddressSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'name', 'cpf', 'phone', 
            'avatar', 'is_active', 'is_staff', 'created_at', 
            'updated_at', 'addresses'
        )
        read_only_fields = ('id', 'is_active', 'is_staff', 'created_at', 'updated_at')

    def to_representation(self, instance):
        """
        Formata a URL do avatar para incluir o domínio completo.
        """
        data = super().to_representation(instance)
        if data.get('avatar'):
            request = self.context.get('request')
            if request:
                data['avatar'] = request.build_absolute_uri(instance.avatar.url)
            else:
                data['avatar'] = f"{settings.MEDIA_URL}{instance.avatar}"
        return data