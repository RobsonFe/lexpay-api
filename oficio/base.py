from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Precatorio
from .serializer import PrecatorioSerializer


class BasePrecatorioView(generics.GenericAPIView):
	"""
	Base que centraliza configurações e a lógica de filtro de Marketplace.
	"""
	serializer_class = PrecatorioSerializer
	permission_classes = [permissions.IsAuthenticated]
	
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

	def get_queryset(self):
		"""
		Retorna queryset otimizado e aplica filtros baseados nas Permissions.
		Isso evita repetir código em cada View.
		"""
		queryset = Precatorio.objects.all().select_related(
			'tribunal',
			'ente_devedor',
			'cedente',
			'advogado'
		).prefetch_related('documentos')
		
		for permission in self.get_permissions():
			if hasattr(permission, 'filter_queryset'):
				queryset = permission.filter_queryset(self.request, queryset, self)
		
		return queryset