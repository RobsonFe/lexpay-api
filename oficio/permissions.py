from rest_framework import permissions
from django.db.models import Q
from auth.models import TypeUserChoices
from .models import Precatorio, StatusPrecatorioChoices


class IsOwnerOrAdmin(permissions.BasePermission):
	"""
	Permissão granular para operações em objetos específicos:
	- Admin/Administrador: acesso total.
	- Cedente: acesso aos seus próprios precatórios.
	- Outros: negado para escrita (Broker/Advogado).
	"""
	def has_object_permission(self, request, view, obj):
		if request.user.is_staff or request.user.type_user == TypeUserChoices.ADMINISTRADOR:
			return True
		return obj.cedente == request.user


class MarketplaceViewPermission(permissions.BasePermission):
	"""
	Permissão que controla a visualização de precatórios baseado no tipo de usuário.
	
	Lógica de Marketplace:
	- Admin/Administrador: Vê todos os precatórios
	- Cedente: Vê apenas os seus precatórios
	- Broker/Advogado: Vê os seus + os disponíveis no mercado
	- Outros: Vê apenas os seus (fallback)
	
	Esta permissão não bloqueia o acesso, mas fornece um método
	para filtrar o queryset baseado nas regras de negócio.
	"""
	
	def has_permission(self, request, view):
		"""
		Permite acesso se o usuário estiver autenticado.
		O filtro do queryset será feito pelo método filter_queryset.
		"""
		return request.user and request.user.is_authenticated
	
	def filter_queryset(self, request, queryset, view):
		"""
		Filtra o queryset baseado no tipo de usuário e nas regras de marketplace.
		
		Args:
			request: Objeto request do Django
			queryset: QuerySet base de precatórios
			view: View que está fazendo a requisição
		
		Returns:
			QuerySet filtrado conforme as regras de negócio
		"""
		user = request.user
		
		if user.is_staff or user.type_user == TypeUserChoices.ADMINISTRADOR:
			return queryset
		
		if user.type_user == TypeUserChoices.CEDENTE:
			return queryset.filter(cedente=user)
		
		if user.type_user in [TypeUserChoices.BROKER, TypeUserChoices.ADVOGADO]:
			return queryset.filter(
				Q(cedente=user) | 
				Q(status=StatusPrecatorioChoices.DISPONIVEL)
			)
		
		return queryset.filter(cedente=user)
