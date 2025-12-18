from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import NotFound
from auth.models import User, Address
from auth.serializer import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer, AddressSerializer,
    LoginRequestSerializer, LogoutRequestSerializer
)
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
)
from drf_spectacular.types import OpenApiTypes


@extend_schema(
    tags=["Usuário"],
    summary="Registrar novo usuário",
    description=(
        "Cria um novo usuário no sistema junto com seus endereços em uma única requisição. "
        "A senha deve atender aos critérios de validação do Django e deve ser confirmada no campo password_confirm. "
        "Os endereços são opcionais e podem ser criados durante o registro ou posteriormente."
    ),
    request=UserCreateSerializer,
    responses={
        201: OpenApiResponse(
            response=UserSerializer,
            description="Usuário registrado com sucesso",
            examples=[
                OpenApiExample(
                    name="Sucesso",
                    summary="Resposta com usuário criado",
                    value={
                        "message": "Usuário registrado com sucesso",
                        "result": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "email": "usuario@example.com",
                            "username": "usuario123",
                            "name": "João Silva",
                            "cpf": "12345678901",
                            "phone": "11987654321",
                            "avatar": "http://127.0.0.1:8000/media/avatars/default.png",
                            "is_active": True,
                            "is_staff": False,
                            "created_at": "2025-12-18T12:00:00Z",
                            "updated_at": "2025-12-18T12:00:00Z",
                            "addresses": [
                                {
                                    "id": "660e8400-e29b-41d4-a716-446655440001",
                                    "address": "Rua Exemplo",
                                    "number": "123",
                                    "complement": "Apto 45",
                                    "city": "São Paulo",
                                    "state": "SP",
                                    "zip_code": "01234567",
                                    "created_at": "2025-12-18T12:00:00Z",
                                    "updated_at": "2025-12-18T12:00:00Z",
                                }
                            ],
                        },
                    },
                ),
            ],
        ),
        400: OpenApiResponse(
            description="Erro de validação",
            examples=[
                OpenApiExample(
                    name="Senhas não coincidem",
                    value={
                        "message": "Erro ao registrar usuário",
                        "errors": {
                            "password_confirm": ["As senhas não coincidem."],
                        },
                    },
                ),
                OpenApiExample(
                    name="Email já existe",
                    value={
                        "message": "Erro ao registrar usuário",
                        "errors": {
                            "email": ["user with this email already exists."],
                        },
                    },
                ),
            ],
        ),
    },
    examples=[
        OpenApiExample(
            "Exemplo de request",
            value={
                "email": "usuario@example.com",
                "username": "usuario123",
                "password": "SenhaSegura123!",
                "password_confirm": "SenhaSegura123!",
                "name": "João Silva",
                "cpf": "12345678901",
                "phone": "11987654321",
                "addresses": [
                    {
                        "address": "Rua Exemplo",
                        "number": "123",
                        "complement": "Apto 45",
                        "city": "São Paulo",
                        "state": "SP",
                        "zip_code": "01234567",
                    }
                ],
            },
            request_only=True,
        ),
    ],
)
class RegisterView(APIView):
	"""
	View para registro de usuário.
	Permite criar usuário junto com endereços em uma única requisição.
	"""
	permission_classes = [AllowAny]
	
	def post(self, request):
		serializer = UserCreateSerializer(data=request.data)
		if serializer.is_valid():
			user = serializer.save()
			user_serializer = UserSerializer(user, context={'request': request})
			return Response({
				'message': 'Usuário registrado com sucesso',
				'result': user_serializer.data
			}, status=status.HTTP_201_CREATED)
		return Response({
			'message': 'Erro ao registrar usuário',
			'errors': serializer.errors
		}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(
    tags=["Autenticação"],
    summary="Login de usuário",
    description=(
        "Autentica um usuário no sistema usando email e senha, retornando tokens JWT (access e refresh). "
        "O access token deve ser enviado no header Authorization como 'Bearer {token}' para requisições autenticadas. "
        "O refresh token pode ser usado para obter um novo access token quando o atual expirar."
    ),
    request=LoginRequestSerializer,
    responses={
        200: OpenApiResponse(
            description="Login realizado com sucesso",
            examples=[
                OpenApiExample(
                    name="Sucesso",
                    summary="Resposta com tokens",
                    value={
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczNDU2Nzg0MCwiaWF0IjoxNzM0NDgxNDQwLCJqdGkiOiIxMjM0NTY3ODkwIiwidXNlcl9pZCI6IjU1MGU4NDAwLWUyOWItNDFkNC1hNzE2LTQ0NjY1NTQ0MDAwMCJ9...",
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM0NTY3ODQwLCJpYXQiOjE3MzQ0ODE0NDAsImp0aSI6IjEyMzQ1Njc4OTAiLCJ1c2VyX2lkIjoiNTUwZTg0MDAtZTI5Yi00MWQ0LWE3MTYtNDQ2NjU1NDQwMDAwIn0...",
                    },
                ),
            ],
        ),
        401: OpenApiResponse(
            description="Credenciais inválidas",
            examples=[
                OpenApiExample(
                    name="Credenciais inválidas",
                    value={"error": "Credenciais inválidas"},
                ),
            ],
        ),
        404: OpenApiResponse(
            description="Usuário não encontrado",
            examples=[
                OpenApiExample(
                    name="Usuário não encontrado",
                    value={"error": "Usuário não encontrado"},
                ),
            ],
        ),
    },
    examples=[
        OpenApiExample(
            "Exemplo de request",
            value={
                "email": "usuario@example.com",
                "password": "SenhaSegura123!",
            },
            request_only=True,
        ),
    ],
)
class LoginView(APIView):
	permission_classes = [AllowAny]
	def post(self, request):
		email = request.data.get('email')
		password = request.data.get('password')
		user = User.objects.filter(email=email).first()
		if user is None:
			return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_404_NOT_FOUND)
		if not user.check_password(password):
			return Response({'error': 'Credenciais inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
		if user is not None:
			refresh = RefreshToken.for_user(user)
			return Response({
				'refresh': str(refresh),
				'access': str(refresh.access_token),
			}, status=status.HTTP_200_OK)
		return Response({'error': 'Credenciais inválidas'}, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema(
    tags=["Autenticação"],
    summary="Logout de usuário",
    description=(
        "Realiza logout do usuário autenticado invalidando o refresh token enviado no body da requisição. "
        "O token será adicionado à blacklist e não poderá mais ser usado para obter novos access tokens. "
        "Requer autenticação via Bearer token no header Authorization e o refresh_token deve ser enviado no body."
    ),
    request=LogoutRequestSerializer,
    responses={
        200: OpenApiResponse(
            description="Logout realizado com sucesso",
            examples=[
                OpenApiExample(
                    name="Sucesso",
                    value={"message": "Logout realizado com sucesso"},
                ),
            ],
        ),
        401: OpenApiResponse(
            description="Token inválido",
            examples=[
                OpenApiExample(
                    name="Token inválido",
                    value={"message": "Token inválido"},
                ),
            ],
        ),
    },
    examples=[
        OpenApiExample(
            "Exemplo de request",
            value={
                "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTczNDU2Nzg0MCwiaWF0IjoxNzM0NDgxNDQwLCJqdGkiOiIxMjM0NTY3ODkwIiwidXNlcl9pZCI6IjU1MGU4NDAwLWUyOWItNDFkNC1hNzE2LTQ0NjY1NTQ0MDAwMCJ9...",
            },
            request_only=True,
        ),
    ],
)
class LogoutView(APIView):
	permission_classes = [IsAuthenticated]
	def post(self, request):
		try:
			refresh_token = request.data.get('refresh')
			token = RefreshToken(refresh_token)
			token.blacklist()
			return Response({'message': 'Logout realizado com sucesso'}, status=status.HTTP_200_OK)
		except TokenError:
			return Response({'message': 'Token inválido'}, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema(
    tags=["Usuário"],
    summary="Obter dados do usuário autenticado",
    description=(
        "Retorna os dados completos do usuário autenticado incluindo todos os endereços associados. "
        "Requer autenticação via Bearer token no header Authorization."
    ),
    responses={
        200: OpenApiResponse(
            response=UserSerializer,
            description="Dados do usuário",
            examples=[
                OpenApiExample(
                    name="Sucesso",
                    summary="Resposta com dados do usuário",
                    value={
                        "message": "Usuário autenticado com sucesso",
                        "result": {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "email": "usuario@example.com",
                            "username": "usuario123",
                            "name": "João Silva",
                            "cpf": "12345678901",
                            "phone": "11987654321",
                            "avatar": "http://127.0.0.1:8000/media/avatars/default.png",
                            "is_active": True,
                            "is_staff": False,
                            "created_at": "2025-12-18T12:00:00Z",
                            "updated_at": "2025-12-18T12:00:00Z",
                            "addresses": [
                                {
                                    "id": "660e8400-e29b-41d4-a716-446655440001",
                                    "address": "Rua Exemplo",
                                    "number": "123",
                                    "complement": "Apto 45",
                                    "city": "São Paulo",
                                    "state": "SP",
                                    "zip_code": "01234567",
                                    "created_at": "2025-12-18T12:00:00Z",
                                    "updated_at": "2025-12-18T12:00:00Z",
                                }
                            ],
                        },
                    },
                ),
            ],
        ),
        401: OpenApiTypes.OBJECT,
    },
)
class UserView(APIView):
	"""
	View para CRUD completo do usuário autenticado.
	GET: Retorna dados do usuário com endereços
	PATCH: Atualiza usuário e endereços
	DELETE: Deleta usuário (endereços são deletados em cascade)
	"""
	permission_classes = [IsAuthenticated]
	
	def get(self, request):
		"""
		Retorna os dados do usuário autenticado com todos os endereços.
		"""
		user = request.user
		serializer = UserSerializer(user, context={'request': request})
		return Response({
			'message': 'Usuário autenticado com sucesso',
			'result': serializer.data
		}, status=status.HTTP_200_OK)

	@extend_schema(
		tags=["Usuário"],
		summary="Atualizar dados do usuário",
		description=(
			"Atualiza os dados do usuário autenticado e seus endereços. "
			"Permite atualizar campos do usuário e gerenciar endereços: criar novos, atualizar existentes (enviando o id) ou manter os existentes. "
			"Requer autenticação via Bearer token no header Authorization."
		),
		request=UserUpdateSerializer,
		responses={
			200: OpenApiResponse(
				response=UserSerializer,
				description="Usuário atualizado com sucesso",
				examples=[
					OpenApiExample(
						name="Sucesso",
						summary="Resposta com usuário atualizado",
						value={
							"message": "Usuário atualizado com sucesso",
							"result": {
								"id": "550e8400-e29b-41d4-a716-446655440000",
								"email": "usuario@example.com",
								"username": "usuario123",
								"name": "João Silva Santos",
								"cpf": "12345678901",
								"phone": "11999999999",
								"avatar": "http://127.0.0.1:8000/media/avatars/default.png",
								"is_active": True,
								"is_staff": False,
								"created_at": "2025-12-18T12:00:00Z",
								"updated_at": "2025-12-18T13:00:00Z",
								"addresses": [],
							},
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
							"message": "Erro ao atualizar usuário",
							"errors": {
								"email": ["user with this email already exists."],
							},
						},
					),
				],
			),
			401: OpenApiTypes.OBJECT,
		},
		examples=[
			OpenApiExample(
				"Exemplo de request",
				value={
					"name": "João Silva Santos",
					"phone": "11999999999",
					"addresses": [
						{
							"id": "660e8400-e29b-41d4-a716-446655440001",
							"address": "Rua Atualizada",
							"number": "789",
						},
						{
							"address": "Novo Endereço",
							"number": "999",
							"city": "Brasília",
							"state": "DF",
							"zip_code": "70000000",
						},
					],
				},
				request_only=True,
			),
		],
	)
	def patch(self, request):
		"""
		Atualiza os dados do usuário e seus endereços.
		Permite atualizar usuário e criar/atualizar/deletar endereços.
		"""
		user = request.user
		serializer = UserUpdateSerializer(user, data=request.data, partial=True, context={'request': request})
		if serializer.is_valid():
			serializer.save()
			user_serializer = UserSerializer(user, context={'request': request})
			return Response({
				'message': 'Usuário atualizado com sucesso',
				'result': user_serializer.data
			}, status=status.HTTP_200_OK)
		return Response({
			'message': 'Erro ao atualizar usuário',
			'errors': serializer.errors
		}, status=status.HTTP_400_BAD_REQUEST)

	@extend_schema(
		tags=["Usuário"],
		summary="Deletar usuário",
		description=(
			"Deleta permanentemente o usuário autenticado e todos os seus endereços associados (CASCADE). "
			"Esta operação é irreversível. Requer autenticação via Bearer token no header Authorization."
		),
		request=None,
		responses={
			204: OpenApiResponse(description="Usuário deletado com sucesso"),
			401: OpenApiTypes.OBJECT,
		},
	)
	def delete(self, request):
		"""
		Deleta o usuário autenticado.
		Os endereços são deletados automaticamente (CASCADE).
		"""
		user = request.user
		user.delete()
		return Response({
			'message': 'Usuário deletado com sucesso'
		}, status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    tags=["Endereço"],
    summary="Listar endereços do usuário",
    description=(
        "Retorna todos os endereços cadastrados do usuário autenticado. "
        "Requer autenticação via Bearer token no header Authorization."
    ),
    responses={
        200: OpenApiResponse(
            description="Endereços listados com sucesso",
            examples=[
                OpenApiExample(
                    name="Sucesso",
                    summary="Resposta com lista de endereços",
                    value={
                        "message": "Endereços listados com sucesso",
                        "result": [
                            {
                                "id": "660e8400-e29b-41d4-a716-446655440001",
                                "address": "Rua Exemplo",
                                "number": "123",
                                "complement": "Apto 45",
                                "city": "São Paulo",
                                "state": "SP",
                                "zip_code": "01234567",
                                "created_at": "2025-12-18T12:00:00Z",
                                "updated_at": "2025-12-18T12:00:00Z",
                            },
                            {
                                "id": "660e8400-e29b-41d4-a716-446655440002",
                                "address": "Avenida Teste",
                                "number": "456",
                                "complement": None,
                                "city": "Rio de Janeiro",
                                "state": "RJ",
                                "zip_code": "20000000",
                                "created_at": "2025-12-18T13:00:00Z",
                                "updated_at": "2025-12-18T13:00:00Z",
                            },
                        ],
                    },
                ),
            ],
        ),
        401: OpenApiTypes.OBJECT,
    },
)
class AddressView(APIView):
	"""
	View para CRUD completo de endereços do usuário autenticado.
	GET: Lista todos os endereços do usuário
	POST: Cria um novo endereço para o usuário
	"""
	permission_classes = [IsAuthenticated]
	
	def get(self, request):
		"""
		Retorna todos os endereços do usuário autenticado.
		"""
		addresses = Address.objects.filter(user=request.user)
		serializer = AddressSerializer(addresses, many=True)
		return Response({
			'message': 'Endereços listados com sucesso',
			'result': serializer.data
		}, status=status.HTTP_200_OK)
	
	@extend_schema(
		tags=["Endereço"],
		summary="Criar novo endereço",
		description=(
			"Cria um novo endereço para o usuário autenticado. "
			"O endereço será automaticamente associado ao usuário que faz a requisição. "
			"Requer autenticação via Bearer token no header Authorization."
		),
		request=AddressSerializer,
		responses={
			201: OpenApiResponse(
				response=AddressSerializer,
				description="Endereço criado com sucesso",
				examples=[
					OpenApiExample(
						name="Sucesso",
						summary="Resposta com endereço criado",
						value={
							"message": "Endereço criado com sucesso",
							"result": {
								"id": "660e8400-e29b-41d4-a716-446655440001",
								"address": "Rua Exemplo",
								"number": "123",
								"complement": "Apto 45",
								"city": "São Paulo",
								"state": "SP",
								"zip_code": "01234567",
								"created_at": "2025-12-18T12:00:00Z",
								"updated_at": "2025-12-18T12:00:00Z",
							},
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
							"message": "Erro ao criar endereço",
							"errors": {
								"state": ["Ensure this field has no more than 2 characters."],
							},
						},
					),
				],
			),
			401: OpenApiTypes.OBJECT,
		},
		examples=[
			OpenApiExample(
				"Exemplo de request",
				value={
					"address": "Rua Exemplo",
					"number": "123",
					"complement": "Apto 45",
					"city": "São Paulo",
					"state": "SP",
					"zip_code": "01234567",
				},
				request_only=True,
			),
		],
	)
	def post(self, request):
		"""
		Cria um novo endereço para o usuário autenticado.
		"""
		serializer = AddressSerializer(data=request.data)
		if serializer.is_valid():
			address = serializer.save(user=request.user)
			return Response({
				'message': 'Endereço criado com sucesso',
				'result': AddressSerializer(address).data
			}, status=status.HTTP_201_CREATED)
		return Response({
			'message': 'Erro ao criar endereço',
			'errors': serializer.errors
		}, status=status.HTTP_400_BAD_REQUEST)


class AddressDetailView(APIView):
	"""
	View para operações específicas em um endereço.
	GET: Retorna um endereço específico
	PATCH: Atualiza um endereço específico
	DELETE: Deleta um endereço específico
	"""
	permission_classes = [IsAuthenticated]
	
	def get_object(self, address_id, user):
		"""
		Retorna o endereço se pertencer ao usuário, caso contrário levanta exceção.
		"""
		try:
			address = Address.objects.get(id=address_id, user=user)
			return address
		except Address.DoesNotExist:
			raise NotFound('Endereço não encontrado')
	
	@extend_schema(
		tags=["Endereço"],
		summary="Obter endereço específico",
		description=(
			"Retorna os dados de um endereço específico do usuário autenticado. "
			"O endereço_id na URL deve ser o UUID do endereço. "
			"Valida que o endereço pertence ao usuário autenticado. "
			"Requer autenticação via Bearer token no header Authorization."
		),
		parameters=[
			OpenApiParameter(
				"address_id",
				OpenApiTypes.UUID,
				OpenApiParameter.PATH,
				description="UUID do endereço",
			),
		],
		responses={
			200: OpenApiResponse(
				response=AddressSerializer,
				description="Endereço encontrado",
				examples=[
					OpenApiExample(
						name="Sucesso",
						summary="Resposta com endereço",
						value={
							"message": "Endereço encontrado com sucesso",
							"result": {
								"id": "660e8400-e29b-41d4-a716-446655440001",
								"address": "Rua Exemplo",
								"number": "123",
								"complement": "Apto 45",
								"city": "São Paulo",
								"state": "SP",
								"zip_code": "01234567",
								"created_at": "2025-12-18T12:00:00Z",
								"updated_at": "2025-12-18T12:00:00Z",
							},
						},
					),
				],
			),
			404: OpenApiResponse(
				description="Endereço não encontrado",
				examples=[
					OpenApiExample(
						name="Não encontrado",
						value={"detail": "Endereço não encontrado"},
					),
				],
			),
			401: OpenApiTypes.OBJECT,
		},
	)
	def get(self, request, address_id):
		"""
		Retorna um endereço específico do usuário autenticado.
		"""
		address = self.get_object(address_id, request.user)
		serializer = AddressSerializer(address)
		return Response({
			'message': 'Endereço encontrado com sucesso',
			'result': serializer.data
		}, status=status.HTTP_200_OK)
	
	@extend_schema(
		tags=["Endereço"],
		summary="Atualizar endereço específico",
		description=(
			"Atualiza os dados de um endereço específico do usuário autenticado. "
			"O endereço_id na URL deve ser o UUID do endereço. "
			"Valida que o endereço pertence ao usuário autenticado. "
			"Requer autenticação via Bearer token no header Authorization."
		),
		parameters=[
			OpenApiParameter(
				"address_id",
				OpenApiTypes.UUID,
				OpenApiParameter.PATH,
				description="UUID do endereço",
			),
		],
		request=AddressSerializer,
		responses={
			200: OpenApiResponse(
				response=AddressSerializer,
				description="Endereço atualizado com sucesso",
				examples=[
					OpenApiExample(
						name="Sucesso",
						summary="Resposta com endereço atualizado",
						value={
							"message": "Endereço atualizado com sucesso",
							"result": {
								"id": "660e8400-e29b-41d4-a716-446655440001",
								"address": "Rua Atualizada",
								"number": "789",
								"complement": "Apto 100",
								"city": "São Paulo",
								"state": "SP",
								"zip_code": "01234567",
								"created_at": "2025-12-18T12:00:00Z",
								"updated_at": "2025-12-18T14:00:00Z",
							},
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
							"message": "Erro ao atualizar endereço",
							"errors": {
								"state": ["Ensure this field has no more than 2 characters."],
							},
						},
					),
				],
			),
			404: OpenApiResponse(
				description="Endereço não encontrado",
				examples=[
					OpenApiExample(
						name="Não encontrado",
						value={"detail": "Endereço não encontrado"},
					),
				],
			),
			401: OpenApiTypes.OBJECT,
		},
		examples=[
			OpenApiExample(
				"Exemplo de request",
				value={
					"address": "Rua Atualizada",
					"number": "789",
					"complement": "Apto 100",
				},
				request_only=True,
			),
		],
	)
	def patch(self, request, address_id):
		"""
		Atualiza um endereço específico do usuário autenticado.
		"""
		address = self.get_object(address_id, request.user)
		serializer = AddressSerializer(address, data=request.data, partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response({
				'message': 'Endereço atualizado com sucesso',
				'result': serializer.data
			}, status=status.HTTP_200_OK)
		return Response({
			'message': 'Erro ao atualizar endereço',
			'errors': serializer.errors
		}, status=status.HTTP_400_BAD_REQUEST)
	
	@extend_schema(
		tags=["Endereço"],
		summary="Deletar endereço específico",
		description=(
			"Deleta permanentemente um endereço específico do usuário autenticado. "
			"O endereço_id na URL deve ser o UUID do endereço. "
			"Valida que o endereço pertence ao usuário autenticado. "
			"Esta operação é irreversível. Requer autenticação via Bearer token no header Authorization."
		),
		parameters=[
			OpenApiParameter(
				"address_id",
				OpenApiTypes.UUID,
				OpenApiParameter.PATH,
				description="UUID do endereço",
			),
		],
		request=None,
		responses={
			204: OpenApiResponse(description="Endereço deletado com sucesso"),
			404: OpenApiResponse(
				description="Endereço não encontrado",
				examples=[
					OpenApiExample(
						name="Não encontrado",
						value={"detail": "Endereço não encontrado"},
					),
				],
			),
			401: OpenApiTypes.OBJECT,
		},
	)
	def delete(self, request, address_id):
		"""
		Deleta um endereço específico do usuário autenticado.
		"""
		address = self.get_object(address_id, request.user)
		address.delete()
		return Response({
			'message': 'Endereço deletado com sucesso'
		}, status=status.HTTP_204_NO_CONTENT)
