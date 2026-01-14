from rest_framework import generics
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError
from due.permissions import IsBrokerOrAdmin, IsAdministradorOrAdvogado
from due.models import DueDiligence, TypeUserChoices
from due.serializer import DueDiligenceSerializer, DueDiligenceCreateSerializer
from auth.models import TypeUserChoices

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiExample,
    OpenApiResponse,
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
class DueCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdministradorOrAdvogado]
    serializer_class = DueDiligenceCreateSerializer
    queryset = DueDiligence.objects.all()

    def get_queryset(self):
        return DueDiligence.objects.select_related('analista','precatorio').all()

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
    put=extend_schema(
        summary="Atualizar Diligência",
        description="Atualizar diligência.",
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
    permission_classes = [IsBrokerOrAdmin | IsAdministradorOrAdvogado]
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
    permission_classes = [IsAdministradorOrAdvogado]
    serializer_class = DueDiligenceCreateSerializer
    queryset = DueDiligence.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        try:
            serializer.save(analista=user)
        except IntegrityError:
            raise ValidationError({'error':'Diligencia já cadastrada no sistema'})