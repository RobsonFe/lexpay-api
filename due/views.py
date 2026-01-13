from rest_framework import generics
from due.permissions import IsBrokerOrAdmin, IsAdministradorOrAdvogado
from due.models import DueDiligence, TypeUserChoices
from due.serializer import DueDiligenceSerializer, DueDiligenceCreateSerializer
from auth.models import TypeUserChoices

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiResponse,
)

@extend_schema_view(
    post=extend_schema(
        summary="Criar Due Diligence (Master/Advogado)",
        description="Endpoint exclusivo para criação de diligências por perfis Master ou Advogado. Utiliza um serializer simplificado para criação.",
        responses={
            201: DueDiligenceCreateSerializer,
            400: OpenApiResponse(description="Erro de validação nos campos enviados."),
            403: OpenApiResponse(description="Usuário não possui permissão (Apenas Master ou Advogado)."),
        },
        tags=["Due Diligence - Gestão"]
    ),
    get=extend_schema(
        summary="Listar Todas as Diligências (Visão Administrativa)",
        description="Retorna uma lista completa de diligências otimizada com select_related.",
        responses={200: DueDiligenceCreateSerializer(many=True)},
        tags=["Due Diligence - Gestão"]
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
        summary="Listar Minhas Diligências",
        description="Retorna as diligências associadas ao usuário logado (Broker). Se o usuário for Administrador, retorna todas.",
        responses={200: DueDiligenceSerializer(many=True)},
        tags=["Due Diligence - Operacional"]
    ),
    post=extend_schema(
        summary="Criar Nova Diligência (Operacional)",
        description="Cria uma nova diligência e a associa automaticamente ao usuário logado (campo 'analista').",
        responses={
            201: DueDiligenceSerializer,
            400: OpenApiResponse(description="Dados inválidos."),
            403: OpenApiResponse(description="Permissão negada."),
        },
        tags=["Due Diligence - Operacional"]
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
        description="Retorna os detalhes completos de uma diligência específica, incluindo dados aninhados do precatório, tribunal e ente.",
        tags=["Due Diligence - Operacional"]
    ),
    put=extend_schema(
        summary="Atualizar Diligência (Completa)",
        description="Atualiza todos os campos permitidos da diligência.",
        tags=["Due Diligence - Operacional"]
    ),
    patch=extend_schema(
        summary="Atualizar Diligência (Parcial)",
        description="Atualiza parcialmente campos da diligência (ex: alterar status ou observações).",
        tags=["Due Diligence - Operacional"]
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
