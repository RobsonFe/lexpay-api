from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import NotFound
from auth.models import User, Address
from auth.serializer import UserSerializer, UserCreateSerializer, UserUpdateSerializer, AddressSerializer


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
	
	def delete(self, request, address_id):
		"""
		Deleta um endereço específico do usuário autenticado.
		"""
		address = self.get_object(address_id, request.user)
		address.delete()
		return Response({
			'message': 'Endereço deletado com sucesso'
		}, status=status.HTTP_204_NO_CONTENT)
