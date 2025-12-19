from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from oficio.serializer import PrecatorioSerializer

class BasePrecatorioView(generics.GenericAPIView):
    """
    Esta classe serve apenas para centralizar a lógica de QuerySet (Marketplace)
    e Filtros, para não repetirmos código nas 5 views abaixo.
    """
    serializer_class = PrecatorioSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Configuração de Filtros (Compartilhada entre List e Retrieve)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'status': ['exact'],
        'tribunal': ['exact'],
        'ente_devedor': ['exact'],
        'natureza': ['exact'],
        'ano_orcamentario': ['exact', 'gte', 'lte'],
        'valor_principal': ['gte', 'lte'],
    }
    search_fields = ['numero_processo', 'descricao']
    ordering_fields = ['valor_principal', 'created_at', 'ano_orcamentario']
    ordering = ['-created_at']