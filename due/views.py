from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError, NotFound
from django.db import IntegrityError
from due.permissions import (IsBrokerOrAdmin, IsAdminOrAdvogado, IsAdminBrokerOrAdvogado, IsAdmin)
from due.models import DueDiligence, TypeUserChoices
from due.serializer import DueDiligenceSerializer, DueDiligenceCreateSerializer
from auth.models import TypeUserChoices

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
    OpenApiTypes
)

@extend_schema_view(
    post=extend_schema(
        summary="Criar Due Diligence (Admin/Advogado)",
        description="Criação de diligências somente para Admin ou Advogado.",
        responses={
            201: DueDiligenceCreateSerializer,
            400: OpenApiResponse(description="Erro de validação nos campos enviados."),
            403: OpenApiResponse(description="Permissão negada para o usuário."),
        },
        tags=["Due Diligence"]
    ),
    get=extend_schema(
        summary="Listar todas as Diligências",
        description="Lista com todas de diligências.",
        responses={200: DueDiligenceCreateSerializer(many=True)},
        tags=["Due Diligence"]
    ),
)
class DueListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrAdvogado]
    serializer_class = DueDiligenceCreateSerializer
    queryset = DueDiligence.objects.all()

    def get_queryset(self):
        return DueDiligence.objects.select_related('analista','precatorio').all()
    

@extend_schema(
    summary="Edição de Diligencias - Admin",
    description="Somente usuários Admin podem realizer alterações nas diligencias.",
    tags=["Due Diligence"],
    responses={
        200: OpenApiResponse(
            response=DueDiligenceSerializer,
            description='Diligencia atualizada com sucesso'
            ),
        401: OpenApiResponse(
            description="Não autenticado"
        ),
        403: OpenApiResponse(
            description="Você não tem permissão para editar diligencias"
        ),
        404: OpenApiResponse(
            description="Diligencia não localizada na base."
        )
    }
)
class DueUpdateView(generics.UpdateAPIView):
    queryset = DueDiligence.objects.all()
    permission_classes = [IsAdmin]
    serializer_class = DueDiligenceSerializer
    http_method_names = ['patch']

    def update(self, request, *args, **kwargs):
        try:
           response = super().update(request, *args, **kwargs)
           return Response(
               {
                "message": "Diligencia ataualizada com sucesso",
                "result": response.data
               }, status=status.HTTP_200_OK
           )
        except ValidationError as e:
            return Response(
                {
                "message": "Erro de validação",
                "erros": e.detail
                },status=status.HTTP_400_BAD_REQUEST
            )
        except NotFound:
            return Response(
                {
                "message":"Diligencia não localizada"
                },
                status=status.HTTP_404_NOT_FOUND
            )
            



@extend_schema_view(
    get=extend_schema(
        summary="Listar Diligências por usuário",
        description="Lista as diligências do usuário que solicita, caso o usuário seja Administrador, consegue ver tudo.",
        responses={200: DueDiligenceSerializer(many=True)},
        tags=["Due Diligence"]
    ),
    post=extend_schema(
        summary="Criar Diligência",
        description="Cria uma diligência e popula ao usuário logado (campo 'analista').",
        responses={
            201: DueDiligenceSerializer,
            400: OpenApiResponse(description="Dados inválidos."),
            403: OpenApiResponse(description="Permissão negada."),
        },
        tags=["Due Diligence"]
    ),
)
class DueDiligenceListCreateView(generics.ListCreateAPIView):
    serializer_class = DueDiligenceSerializer
    permission_classes = [IsBrokerOrAdmin]
    queryset = DueDiligence.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.type_user == TypeUserChoices.ADMINISTRADOR:
            return DueDiligence.objects.all()
        return DueDiligence.objects.filter(analista=user)
    
    def perform_create(self, serializer):
        serializer.save(analista=self.request.user)

@extend_schema_view(
    get=extend_schema(
        summary="Detalhar Diligência",
        description="Retorna uma diligência específica.",
        tags=["Due Diligence"]
    ),
    patch=extend_schema(
        summary="Atualizar Diligência-PATCH",
        description="Atualiza parcialmente campos.",
        tags=["Due Diligence"]
    )
)
class DueDiligenceRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = DueDiligenceSerializer
    permission_classes = [IsAdminBrokerOrAdvogado]
    queryset = DueDiligence.objects.all()

    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        queryset = DueDiligence.objects.select_related(
            'precatorio', 'analista', 'precatorio__tribunal', 'precatorio__ente_devedor'
        )

        is_admin = user.is_staff or (user.type_user == TypeUserChoices.ADMINISTRADOR)

        if is_admin:
            return queryset.all()
        return queryset.filter(analista=user)

@extend_schema(
    summary="Criar Diligencias Admin/Adv",
    description="Criaçao de diligencias somente para  - Admin/Adv",
    tags=["Due Diligence"],
    request=DueDiligenceCreateSerializer,
    responses={
        201: OpenApiResponse(
            description="Diligencia criada com sucesso",
            response=DueDiligenceCreateSerializer,
            examples=[
                OpenApiExample(
                name="Criado com sucesso",
                summary="Requisição foi criada com sucesso.",
                value={
                    "id": "1d54a382-f053-40c3-a481-75c4bb743728",
                    "precatorio": "550e8400-e29b-41d4-a716-446655440000",
                    "prioridade": "ALTA",
                    "analista": "4f1fc912-3111-461e-8094-0aef157cdbe6",
                    "observacoes": "Observação referente a due.",
                    "status_analise": "PENDENTE",
                    "created_at": "2026-01-14"
                    }
                )
            ]
        ),
        400: OpenApiResponse(
            description="Erro de validação",
            examples=[
                OpenApiExample(
                    name="Erro de validação",
                    summary="Precátorio já esta em análise",
                    value={
                        "precatorio":["Esse precatório já esta em diligencia."]
                    }
                )       
            ]
        ),
    }
)
class DueCreateView(generics.CreateAPIView):
    permission_classes = [IsAdminOrAdvogado]
    serializer_class = DueDiligenceCreateSerializer
    queryset = DueDiligence.objects.all()
    
    def create(self, request, *args, **kwargs):
        try:
            """Invoca o metôdo pai de CreateAPIView e encaminha o resquest para que seja feita a mentagem o Response"""
            response = super().create(request, *args, **kwargs)
            return Response(
                {
                    "message": "Due Diligence criada com sucesso",
                    "result": response.data
                },
                status=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return Response(
                {
                    "message": "Erro de validação",
                    "errors": e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except IntegrityError:
            return Response(
                {
                    "message": "Erro ao criar due diligence", 
                    "errors": {
                        "precatorio": ["Já existe uma Due Diligence ativa para este precatório."]
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        user = self.request.user
        try:
            serializer.save(analista=user)
        except IntegrityError:
            raise ValidationError({'error':'Diligencia já cadastrada no sistema'})