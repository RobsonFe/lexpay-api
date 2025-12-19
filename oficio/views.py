from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from django.db import transaction
from drf_spectacular.utils import (
	extend_schema,
	OpenApiParameter,
	OpenApiExample,
	OpenApiResponse,
)
from drf_spectacular.types import OpenApiTypes

from .base import BasePrecatorioView
from .permissions import IsOwnerOrAdmin, MarketplaceViewPermission
from .models import Precatorio
from .serializer import PrecatorioSerializer, PrecatorioUpdateSerializer


class PrecatorioListView(BasePrecatorioView, generics.ListAPIView):
	"""
	View para listar precatórios com filtros e paginação.
	
	A lógica de marketplace é controlada pela permissão MarketplaceViewPermission.
	"""
	permission_classes = [MarketplaceViewPermission]
	
	@extend_schema(
		tags=['Precatórios'],
		summary="Listar Precatórios",
		description=(
			"Retorna lista paginada de precatórios com filtros e busca. "
			"A visibilidade dos precatórios depende do tipo de usuário: "
			"Administradores veem todos, Cedentes veem apenas os seus, "
			"Brokers e Advogados veem os seus próprios mais os disponíveis no mercado."
		),
		parameters=[
			OpenApiParameter(
				name='status',
				type=OpenApiTypes.STR,
				location=OpenApiParameter.QUERY,
				description="Filtrar por status (Em Análise, Disponível, Em Negociação, Vendido, Suspenso)",
			),
			OpenApiParameter(
				name='natureza',
				type=OpenApiTypes.STR,
				location=OpenApiParameter.QUERY,
				description="Filtrar por natureza (Alimentar, Comum)",
			),
			OpenApiParameter(
				name='tribunal',
				type=OpenApiTypes.UUID,
				location=OpenApiParameter.QUERY,
				description="Filtrar por tribunal (UUID)",
			),
			OpenApiParameter(
				name='ente_devedor',
				type=OpenApiTypes.UUID,
				location=OpenApiParameter.QUERY,
				description="Filtrar por ente devedor (UUID)",
			),
			OpenApiParameter(
				name='ano_orcamentario',
				type=OpenApiTypes.INT,
				location=OpenApiParameter.QUERY,
				description="Filtrar por ano orçamentário",
			),
			OpenApiParameter(
				name='valor_principal__gte',
				type=OpenApiTypes.DECIMAL,
				location=OpenApiParameter.QUERY,
				description="Valor principal maior ou igual a",
			),
			OpenApiParameter(
				name='valor_principal__lte',
				type=OpenApiTypes.DECIMAL,
				location=OpenApiParameter.QUERY,
				description="Valor principal menor ou igual a",
			),
			OpenApiParameter(
				name='search',
				type=OpenApiTypes.STR,
				location=OpenApiParameter.QUERY,
				description="Buscar por número do processo ou descrição",
			),
		],
		responses={
			200: OpenApiResponse(
				description="Lista de precatórios retornada com sucesso",
				response=PrecatorioSerializer,
				examples=[
					OpenApiExample(
						name="Sucesso",
						summary="Resposta com lista de precatórios",
						value={
							"message": "Precatórios listados com sucesso",
							"count": 10,
							"next": "http://127.0.0.1:8000/api/v1/oficio/precatorios/listar/?page=2",
							"previous": None,
							"results": [
								{
									"id": "550e8400-e29b-41d4-a716-446655440000",
									"numero_processo": "0000123-45.2023.4.01.0001",
									"natureza": "Alimentar",
									"natureza_display": "Alimentar",
									"valor_principal": "500000.00",
									"valor_venda": "450000.00",
									"percentual_honorarios": "10.00",
									"data_expedicao": "2023-01-15",
									"ano_orcamentario": 2024,
									"status": "Disponível",
									"status_display": "Disponível",
									"descricao": "Precatório alimentar do estado de São Paulo",
									"tribunal": {
										"id": "660e8400-e29b-41d4-a716-446655440001",
										"nome": "Tribunal Regional Federal da 1ª Região",
										"sigla": "TRF1",
										"uf": "DF"
									},
									"ente_devedor": {
										"id": "770e8400-e29b-41d4-a716-446655440002",
										"nome": "Fazenda Pública do Estado de São Paulo",
										"cnpj": "12345678000190",
										"esfera": "Estadual"
									},
									"cedente": {
										"id": "880e8400-e29b-41d4-a716-446655440003",
										"name": "João Silva",
										"email": "joao@example.com",
										"type_user": "Cedente",
										"avatar": None
									},
									"advogado": None,
									"documentos": [],
									"created_at": "2023-01-15T10:00:00Z",
									"updated_at": "2023-01-15T10:00:00Z"
								}
							]
						},
					),
				],
			),
			401: OpenApiResponse(description="Não autenticado"),
		}
	)
	def get(self, request, *args, **kwargs):
		"""
		Método GET: Retorna lista paginada e filtrada de precatórios.
		"""
		try:
			queryset = self.filter_queryset(self.get_queryset())
			page = self.paginate_queryset(queryset)
			
			if page is not None:
				serializer = self.get_serializer(page, many=True)
				paginated_response = self.get_paginated_response(serializer.data)
				
				return Response({
					'message': 'Precatórios listados com sucesso',
					'count': paginated_response.data.get('count', 0),
					'next': paginated_response.data.get('next'),
					'previous': paginated_response.data.get('previous'),
					'results': paginated_response.data.get('results', [])
				}, status=status.HTTP_200_OK)
			
			serializer = self.get_serializer(queryset, many=True)
			return Response({
				'message': 'Precatórios listados com sucesso',
				'results': serializer.data
			}, status=status.HTTP_200_OK)
			
		except Exception as e:
			return Response(
				{
					'message': 'Erro ao listar precatórios',
					'error': str(e)
				},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


class PrecatorioCreateView(BasePrecatorioView, generics.CreateAPIView):
	"""
	View para criar um novo precatório.
	Apenas usuários autenticados podem criar precatórios.
	"""
	
	@extend_schema(
		tags=['Precatórios'],
		summary="Criar Precatório",
		description=(
			"Cria um novo precatório no sistema. O usuário logado será automaticamente "
			"definido como cedente. É necessário informar tribunal_id e ente_devedor_id "
			"que devem existir no sistema. O número do processo deve ser único."
		),
		request=PrecatorioSerializer,
		responses={
			201: OpenApiResponse(
				description="Precatório criado com sucesso",
				response=PrecatorioSerializer,
				examples=[
					OpenApiExample(
						name="Sucesso",
						summary="Resposta com precatório criado",
						value={
							"message": "Precatório criado com sucesso",
							"result": {
								"id": "550e8400-e29b-41d4-a716-446655440000",
								"numero_processo": "0000123-45.2023.4.01.0001",
								"natureza": "Alimentar",
								"natureza_display": "Alimentar",
								"valor_principal": "500000.00",
								"valor_venda": "450000.00",
								"percentual_honorarios": "10.00",
								"data_expedicao": "2023-01-15",
								"ano_orcamentario": 2024,
								"status": "Em Análise",
								"status_display": "Em Análise",
								"descricao": "Precatório alimentar",
								"tribunal": {
									"id": "660e8400-e29b-41d4-a716-446655440001",
									"nome": "TRF1",
									"sigla": "TRF1",
									"uf": "DF"
								},
								"ente_devedor": {
									"id": "770e8400-e29b-41d4-a716-446655440002",
									"nome": "Fazenda Pública do Estado de São Paulo",
									"cnpj": "12345678000190",
									"esfera": "Estadual"
								},
								"cedente": {
									"id": "880e8400-e29b-41d4-a716-446655440003",
									"name": "João Silva",
									"email": "joao@example.com",
									"type_user": "Cedente",
									"avatar": None
								},
								"advogado": None,
								"documentos": [],
								"created_at": "2023-01-15T10:00:00Z",
								"updated_at": "2023-01-15T10:00:00Z"
							}
						},
					),
				],
			),
			400: OpenApiResponse(
				description="Erro de validação",
				examples=[
					OpenApiExample(
						name="Número de processo duplicado",
						value={
							"message": "Erro ao criar precatório",
							"errors": {
								"numero_processo": ["precatorio with this numero processo already exists."]
							}
						},
					),
					OpenApiExample(
						name="Tribunal inválido",
						value={
							"message": "Erro ao criar precatório",
							"errors": {
								"tribunal_id": ["Invalid pk \"invalid-uuid\" - object does not exist."]
							}
						},
					),
				],
			),
			401: OpenApiResponse(description="Não autenticado"),
		},
		examples=[
			OpenApiExample(
				"Exemplo de request",
				value={
					"numero_processo": "0000123-45.2023.4.01.0001",
					"natureza": "Alimentar",
					"valor_principal": "500000.00",
					"valor_venda": "450000.00",
					"percentual_honorarios": "10.00",
					"data_expedicao": "2023-01-15",
					"ano_orcamentario": 2024,
					"status": "Em Análise",
					"descricao": "Precatório alimentar do estado de São Paulo",
					"tribunal_id": "660e8400-e29b-41d4-a716-446655440001",
					"ente_devedor_id": "770e8400-e29b-41d4-a716-446655440002"
				},
				request_only=True,
			),
		],
	)
	def post(self, request, *args, **kwargs):
		"""
		Método POST: Cria um novo precatório.
		"""
		try:
			serializer = self.get_serializer(data=request.data)
			
			if not serializer.is_valid():
				return Response(
					{
						'message': 'Erro ao criar precatório',
						'errors': serializer.errors
					},
					status=status.HTTP_400_BAD_REQUEST
				)
			
			with transaction.atomic():
				precatorio = serializer.save(cedente=request.user)
			
			precatorio.refresh_from_db()
			response_serializer = PrecatorioSerializer(
				precatorio,
				context={'request': request}
			)
			
			return Response(
				{
					'message': 'Precatório criado com sucesso',
					'result': response_serializer.data
				},
				status=status.HTTP_201_CREATED
			)
			
		except ValidationError as e:
			return Response(
				{
					'message': 'Erro de validação ao criar precatório',
					'errors': e.detail if hasattr(e, 'detail') else str(e)
				},
				status=status.HTTP_400_BAD_REQUEST
			)
		except Exception as e:
			return Response(
				{
					'message': 'Erro ao criar precatório',
					'error': str(e)
				},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


class PrecatorioRetrieveView(BasePrecatorioView, generics.RetrieveAPIView):
	"""
	View para obter detalhes de um precatório específico.
	
	A lógica de marketplace é controlada pela permissão MarketplaceViewPermission.
	"""
	permission_classes = [MarketplaceViewPermission]
	
	@extend_schema(
		tags=['Precatórios'],
		summary="Obter Detalhes do Precatório",
		description=(
			"Retorna os dados completos de um precatório específico incluindo "
			"tribunal, ente devedor, cedente, advogado e todos os documentos associados. "
			"A visibilidade depende das permissões do usuário."
		),
		parameters=[
			OpenApiParameter(
				name='pk',
				type=OpenApiTypes.UUID,
				location=OpenApiParameter.PATH,
				description="UUID do precatório",
			),
		],
		responses={
			200: OpenApiResponse(
				description="Precatório encontrado",
				response=PrecatorioSerializer,
				examples=[
					OpenApiExample(
						name="Sucesso",
						summary="Resposta com precatório completo",
						value={
							"message": "Precatório encontrado com sucesso",
							"result": {
								"id": "550e8400-e29b-41d4-a716-446655440000",
								"numero_processo": "0000123-45.2023.4.01.0001",
								"natureza": "Alimentar",
								"natureza_display": "Alimentar",
								"valor_principal": "500000.00",
								"valor_venda": "450000.00",
								"percentual_honorarios": "10.00",
								"data_expedicao": "2023-01-15",
								"ano_orcamentario": 2024,
								"status": "Disponível",
								"status_display": "Disponível",
								"descricao": "Precatório alimentar",
								"tribunal": {
									"id": "660e8400-e29b-41d4-a716-446655440001",
									"nome": "TRF1",
									"sigla": "TRF1",
									"uf": "DF"
								},
								"ente_devedor": {
									"id": "770e8400-e29b-41d4-a716-446655440002",
									"nome": "Fazenda Pública do Estado de São Paulo",
									"cnpj": "12345678000190",
									"esfera": "Estadual"
								},
								"cedente": {
									"id": "880e8400-e29b-41d4-a716-446655440003",
									"name": "João Silva",
									"email": "joao@example.com",
									"type_user": "Cedente",
									"avatar": None
								},
								"advogado": None,
								"documentos": [
									{
										"id": "990e8400-e29b-41d4-a716-446655440004",
										"titulo": "Ofício Requisitório",
										"arquivo": "http://127.0.0.1:8000/media/precatorios/docs/2023/01/oficio.pdf",
										"enviado_em": "2023-01-15T10:00:00Z",
										"extension": ".pdf",
										"size_mb": 2.5
									}
								],
								"created_at": "2023-01-15T10:00:00Z",
								"updated_at": "2023-01-15T10:00:00Z"
							}
						},
					),
				],
			),
			404: OpenApiResponse(
				description="Precatório não encontrado",
				examples=[
					OpenApiExample(
						name="Não encontrado",
						value={
							"message": "Precatório não encontrado"
						},
					),
				],
			),
			403: OpenApiResponse(
				description="Sem permissão",
				examples=[
					OpenApiExample(
						name="Sem permissão",
						value={
							"message": "Você não tem permissão para visualizar este precatório"
						},
					),
				],
			),
			401: OpenApiResponse(description="Não autenticado"),
		}
	)
	def get(self, request, *args, **kwargs):
		"""
		Método GET: Retorna os dados completos de um único precatório.
		"""
		try:
			precatorio = self.get_object()
			serializer = self.get_serializer(precatorio)
			
			return Response(
				{
					'message': 'Precatório encontrado com sucesso',
					'result': serializer.data
				},
				status=status.HTTP_200_OK
			)
			
		except NotFound:
			return Response(
				{
					'message': 'Precatório não encontrado'
				},
				status=status.HTTP_404_NOT_FOUND
			)
		except PermissionDenied:
			return Response(
				{
					'message': 'Você não tem permissão para visualizar este precatório'
				},
				status=status.HTTP_403_FORBIDDEN
			)
		except Exception as e:
			return Response(
				{
					'message': 'Erro ao obter precatório',
					'error': str(e)
				},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


class PrecatorioUpdateView(BasePrecatorioView, generics.UpdateAPIView):
	"""
	View para atualizar um precatório existente.
	Usa apenas PATCH (atualização parcial).
	Requer permissão de dono ou administrador.
	"""
	
	serializer_class = PrecatorioUpdateSerializer
	permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
	http_method_names = ['patch']
	
	@extend_schema(
		tags=['Precatórios'],
		summary="Atualizar Precatório",
		description=(
			"Atualiza dados de um precatório existente usando PATCH (atualização parcial). "
			"Apenas o dono (cedente) ou administrador pode atualizar. "
			"Campos permitidos para atualização: valor_venda, status, descricao, percentual_honorarios. "
			"O número do processo, tribunal e ente devedor não podem ser alterados após a criação."
		),
		parameters=[
			OpenApiParameter(
				name='pk',
				type=OpenApiTypes.UUID,
				location=OpenApiParameter.PATH,
				description="UUID do precatório",
			),
		],
		request=PrecatorioUpdateSerializer,
		responses={
			200: OpenApiResponse(
				description="Precatório atualizado com sucesso",
				response=PrecatorioSerializer,
				examples=[
					OpenApiExample(
						name="Sucesso",
						summary="Resposta com precatório atualizado",
						value={
							"message": "Precatório atualizado com sucesso",
							"result": {
								"id": "550e8400-e29b-41d4-a716-446655440000",
								"numero_processo": "0000123-45.2023.4.01.0001",
								"natureza": "Alimentar",
								"natureza_display": "Alimentar",
								"valor_principal": "500000.00",
								"valor_venda": "400000.00",
								"percentual_honorarios": "12.00",
								"data_expedicao": "2023-01-15",
								"ano_orcamentario": 2024,
								"status": "Em Negociação",
								"status_display": "Em Negociação",
								"descricao": "Precatório atualizado - em negociação",
								"tribunal": {
									"id": "660e8400-e29b-41d4-a716-446655440001",
									"nome": "TRF1",
									"sigla": "TRF1",
									"uf": "DF"
								},
								"ente_devedor": {
									"id": "770e8400-e29b-41d4-a716-446655440002",
									"nome": "Fazenda Pública do Estado de São Paulo",
									"cnpj": "12345678000190",
									"esfera": "Estadual"
								},
								"cedente": {
									"id": "880e8400-e29b-41d4-a716-446655440003",
									"name": "João Silva",
									"email": "joao@example.com",
									"type_user": "Cedente",
									"avatar": None
								},
								"advogado": None,
								"documentos": [],
								"created_at": "2023-01-15T10:00:00Z",
								"updated_at": "2023-01-20T15:30:00Z"
							}
						},
					),
				],
			),
			400: OpenApiResponse(
				description="Erro de validação",
				examples=[
					OpenApiExample(
						name="Erro de validação",
						value={
							"message": "Erro ao atualizar precatório",
							"errors": {
								"status": ["\"Status inválido\" is not a valid choice."]
							}
						},
					),
				],
			),
			403: OpenApiResponse(
				description="Sem permissão",
				examples=[
					OpenApiExample(
						name="Sem permissão",
						value={
							"message": "Você não tem permissão para atualizar este precatório"
						},
					),
				],
			),
			404: OpenApiResponse(
				description="Precatório não encontrado",
				examples=[
					OpenApiExample(
						name="Não encontrado",
						value={
							"message": "Precatório não encontrado"
						},
					),
				],
			),
			401: OpenApiResponse(description="Não autenticado"),
		},
		examples=[
			OpenApiExample(
				"Exemplo de request",
				value={
					"valor_venda": "400000.00",
					"status": "Em Negociação",
					"descricao": "Precatório atualizado - em negociação",
					"percentual_honorarios": "12.00"
				},
				request_only=True,
			),
		],
	)
	def patch(self, request, *args, **kwargs):
		"""
		Método PATCH: Atualiza parcialmente os dados do precatório.
		"""
		try:
			precatorio = self.get_object()
			serializer = self.get_serializer(precatorio, data=request.data, partial=True)
			
			if not serializer.is_valid():
				return Response(
					{
						'message': 'Erro ao atualizar precatório',
						'errors': serializer.errors
					},
					status=status.HTTP_400_BAD_REQUEST
				)
			
			with transaction.atomic():
				precatorio = serializer.save()
			
			precatorio.refresh_from_db()
			response_serializer = PrecatorioSerializer(
				precatorio,
				context={'request': request}
			)
			
			return Response(
				{
					'message': 'Precatório atualizado com sucesso',
					'result': response_serializer.data
				},
				status=status.HTTP_200_OK
			)
			
		except NotFound:
			return Response(
				{
					'message': 'Precatório não encontrado'
				},
				status=status.HTTP_404_NOT_FOUND
			)
		except PermissionDenied:
			return Response(
				{
					'message': 'Você não tem permissão para atualizar este precatório'
				},
				status=status.HTTP_403_FORBIDDEN
			)
		except ValidationError as e:
			return Response(
				{
					'message': 'Erro de validação ao atualizar precatório',
					'errors': e.detail if hasattr(e, 'detail') else str(e)
				},
				status=status.HTTP_400_BAD_REQUEST
			)
		except Exception as e:
			return Response(
				{
					'message': 'Erro ao atualizar precatório',
					'error': str(e)
				},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)


class PrecatorioDeleteView(BasePrecatorioView, generics.DestroyAPIView):
	"""
	View para deletar um precatório.
	Requer permissão de dono ou administrador.
	"""
	
	permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
	
	@extend_schema(
		tags=['Precatórios'],
		summary="Deletar Precatório",
		description=(
			"Remove permanentemente um precatório do sistema. "
			"Apenas o dono (cedente) ou administrador pode deletar. "
			"Esta operação é irreversível e também deletará todos os documentos associados (CASCADE)."
		),
		parameters=[
			OpenApiParameter(
				name='pk',
				type=OpenApiTypes.UUID,
				location=OpenApiParameter.PATH,
				description="UUID do precatório",
			),
		],
		responses={
			204: OpenApiResponse(
				description="Precatório deletado com sucesso",
				examples=[
					OpenApiExample(
						name="Sucesso",
						value={
							"message": "Precatório deletado com sucesso"
						},
					),
				],
			),
			403: OpenApiResponse(
				description="Sem permissão",
				examples=[
					OpenApiExample(
						name="Sem permissão",
						value={
							"message": "Você não tem permissão para deletar este precatório"
						},
					),
				],
			),
			404: OpenApiResponse(
				description="Precatório não encontrado",
				examples=[
					OpenApiExample(
						name="Não encontrado",
						value={
							"message": "Precatório não encontrado"
						},
					),
				],
			),
			401: OpenApiResponse(description="Não autenticado"),
		}
	)
	def delete(self, request, *args, **kwargs):
		"""
		Método DELETE: Remove o precatório permanentemente.
		"""
		try:
			precatorio = self.get_object()
			
			with transaction.atomic():
				precatorio.delete()
			
			return Response(
				{
					'message': 'Precatório deletado com sucesso'
				},
				status=status.HTTP_204_NO_CONTENT
			)
			
		except NotFound:
			return Response(
				{
					'message': 'Precatório não encontrado'
				},
				status=status.HTTP_404_NOT_FOUND
			)
		except PermissionDenied:
			return Response(
				{
					'message': 'Você não tem permissão para deletar este precatório'
				},
				status=status.HTTP_403_FORBIDDEN
			)
		except Exception as e:
			return Response(
				{
					'message': 'Erro ao deletar precatório',
					'error': str(e)
				},
				status=status.HTTP_500_INTERNAL_SERVER_ERROR
			)
