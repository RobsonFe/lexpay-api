from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiExample, extend_schema, OpenApiResponse, extend_schema_view
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from proposal.permissions import IsAdminOrBroker, IsBrokerOrCedenteOrAdmin
from proposal.models import Proposal
from proposal.serializer import ProposalSerializer
from proposal.services import ProposalService
from rest_framework.decorators import action


@extend_schema(
    tags=["Propostas"],
    summary="Calculadora Automática de Propostas",
    description="Calculadora automática de propostas de antecipação de precatórios.",
    responses={
        201: ProposalSerializer,
        400: OpenApiResponse(description="Erro de validação nos dados."),
        401: OpenApiResponse(description="Não autenticado"),
        403: OpenApiResponse(description="Sem permissão."),
    },
    examples=[
        OpenApiExample(
            "Exemplo de Requisição",
            value={
                "precatorio": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "valor_proposto": "80000.00",
                "taxa_desconto": "20.00",
                "taxa_juros_anual": "12.50",
                "prazo_pagamento_meses": 24,
                "data_vencimento": "2026-12-31",
                "observacoes": "Observação sobre a proposta",
            },
            request_only=True,
        )
    ],
)

class CreateProposalView(generics.CreateAPIView):
    permission_classes = [IsBrokerOrCedenteOrAdmin]
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer

    def perform_create(self, serializer):
        if getattr(self, "swagger_fake_view", False):
            return None
        
        user = self.request.user
        if user.type_user not in ["Broker", "Admin"]:
            raise PermissionDenied(
                "Apenas usuários do tipo 'Broker' podem criar propostas de compra."
            )
        try:
            with transaction.atomic():
                proposal = serializer.save(proponente=user)
                proposal._current_user = user
                proposal.status = "ENVIADA"
                proposal.save()
                return Response(
                    {"result": serializer.data}, status=status.HTTP_201_CREATED
                )
        except Exception as e:
            return Response({"error": [str(e)]}, status=status.HTTP_400_BAD_REQUEST)

class ProposalListView(APIView):
    permission_classes = [IsBrokerOrCedenteOrAdmin]
    serializer_class = ProposalSerializer

    @extend_schema(
        tags=["Propostas"],
        request=None,
        summary="Rota Para Listagem de Propostas",
        description= "Lista todas as propostas de antecipação de precatórios. de acordo com o usuário logado.",
        responses={
            200: ProposalSerializer(many=True),
            401: OpenApiResponse(description="Não autenticado"),
            403: OpenApiResponse(description="Sem permissão."),
            404: OpenApiResponse(description="Nada encontrado.")
        },
        examples=[
            OpenApiExample(
                "Exemplo de Retorno com Dados",
                value={
                    "results": [
                        {
                        "id": "357ab638-43c2-425d-b5a9-4f277c39fc84",
                        "precatorio": "3f09ae47-16ef-4c45-ab31-43c53446aaa4",
                        "proponente_nome": "Spatialcaver3",
                        "valor_proposto": "100000.00",
                        "taxa_desconto": "20.00",
                        "taxa_juros_anual": "12.50",
                        "prazo_pagamento_meses": 1,
                        "data_vencimento": "31-12-2026",
                        "observacoes": None,
                        "valor_liquido_cedente": "95000.00",
                        "valor_liquido_proponente": "99013.64",
                        "lucro": "100.00",
                        "status": "RASCUNHO",
                        "created_at": "13-01-2026 11:18",
                        }
                    ]
                },
                response_only=True, 
                status_codes=["200"]
            )
        ]
    )
    def get(self, request):
        user = self.request.user
        try:
            if user.type_user == "Administrador":
                queryset = Proposal.objects.all()
            elif user.type_user == "Broker":
                queryset = Proposal.objects.filter(proponente=user)
            elif user.type_user == "Cedente":
                queryset = Proposal.objects.filter(precatorio__cedente=user)
            serializer = self.serializer_class(queryset, many=True)
            return Response({"results": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProposalUpdateView(APIView):
    permission_classes = [IsAdminOrBroker]

    @extend_schema(
        tags=["Propostas"],
        summary="Rota de Atualização de Propostas",
        request=ProposalSerializer,
        responses={201: ProposalSerializer,
            401: OpenApiResponse(description="Não autenticado"),
            403: OpenApiResponse(description="Sem permissão."),
            404: OpenApiResponse(description="Nada encontrado.")},
        description="Rota para atualização de uma proposta de Antecipação de um precatório, somente Brokers e Administradores podem atualizar propostas.",
        examples=[
            OpenApiExample(
                "Exemplo de Requisição (Brokers e admins)",
                value={
                    "valor_proposto": "100000.00",
                    "taxa_desconto": "20.00",
                    "taxa_juros_anual": "12.50",
                    "prazo_pagamento_meses": 1,
                    "data_vencimento": "31-12-2026",
                    "observacoes": "Atualização de proposta",
                    "status": "ENVIADA",
                },
            )
        ],
    )
    def patch(self, request, pk, *args, **kwargs):
        try:
            proposal = get_object_or_404(Proposal, pk=pk)
            serializer = ProposalSerializer(proposal, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {
                    "message": "Proposta atualizada com sucesso!",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProposalDeleteView(APIView):
    permission_classes = [IsBrokerOrCedenteOrAdmin]

    @extend_schema(
        tags=["Propostas"],
        request=ProposalSerializer,
        summary="Rota de Exclusão de Propostas",
        description="Rota para exclusão de uma proposta de Antecipação de um precatório, somente Brokers e Administradores podem excluir propostas.",
        responses={201: ProposalSerializer,
            401: OpenApiResponse(description="Não autenticado"),
            403: OpenApiResponse(description="Sem permissão."),
            404: OpenApiResponse(description="Nada encontrado.")},
        examples=[
            OpenApiExample(
                "Exemplo de Retorno",
                value={
                   "message": "Proposta deletada com sucesso!"
                },
            )
        ],      
    )
    def delete(self, request, pk, *args, **kwargs):
        try:
            proposal = get_object_or_404(Proposal, pk=pk)
            proposal.delete()
            return Response(
                {"message": "Proposta deletada com sucesso!"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProposalAcceptView(APIView):
    permission_classes = [IsAdminOrBroker]

    @extend_schema(
        tags=["Propostas"],
        summary="Rota para Aceitar Propostas",
        description="Endpoint para aceitar uma proposta. Rejeita automaticamente concorrentes.",
        responses={
            200: ProposalSerializer,
            400: OpenApiResponse(description="O precatório não está mais disponível."),
            401: OpenApiResponse(description="Não autenticado"),
            403: OpenApiResponse(description="Sem permissão."),
            404: OpenApiResponse(description="Nada encontrado.")},
        examples=[
            OpenApiExample(
                "Exemplo de Retorno",
                value={
                    "message": "Proposta aceita e concorrentes rejeitadas com sucesso."
                },
            )
        ],
    )
    def patch(self, request, pk):
        try:
            ProposalService.aceitar_proposta(pk, request.user)
            
            
            return Response(
                {"message": "Proposta aceita e concorrentes rejeitadas."},
                status=status.HTTP_200_OK,
            )
        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Erro crítico: {str(e)}"}, status=500)

class InvestorOpportunitiesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Propostas"],
        summary="Rota para Listar Oportunidades de Investimento",
        description="Lista oportunidades de investimento ordenadas por inteligência de rentabilidade (Score).",
        responses={201: ProposalSerializer,
            401: OpenApiResponse(description="Não autenticado"),
            403: OpenApiResponse(description="Sem permissão."),
            404: OpenApiResponse(description="Nada encontrado.")},
        examples=[
            OpenApiExample(
                "Exemplo de Retorno com Dados",
                value={
                    "results": [
                        {
                        "id": "357ab638-43c2-425d-b5a9-4f277c39fc84",
                        "precatorio": "3f09ae47-16ef-4c45-ab31-43c53446aaa4",
                        "proponente_nome": "Spatialcaver3",
                        "valor_proposto": "100000.00",
                        "taxa_desconto": "20.00",
                        "taxa_juros_anual": "12.50",
                        "prazo_pagamento_meses": 1,
                        "data_vencimento": "31-12-2026",
                        "observacoes": None,
                        "valor_liquido_cedente": "95000.00",
                        "valor_liquido_proponente": "99013.64",
                        "lucro": "100.00",
                        "status": "RASCUNHO",
                        "created_at": "13-01-2026 11:18",
                        }
                    ]
                },
                response_only=True,
                status_codes=["200"]
            )
        ]
    )
    def get(self, request):

        proposals = Proposal.objects.filter(status="ENVIADA").com_score_atratividade()
        serializer = ProposalSerializer(proposals, many=True)
        return Response(
            {"count": proposals.count(), "results": serializer.data},
            status=status.HTTP_200_OK,
        )

@extend_schema_view( 
        show=extend_schema(            
        tags=["Propostas"],
        summary="Rota para Listar propostas [ViewSet]",
        request=None,
        description= "Lista todas as propostas de antecipação de precatórios. de acordo com o usuário logado.",
        responses={
            200: ProposalSerializer(many=True),
            401: OpenApiResponse(description="Não autenticado"),
            403: OpenApiResponse(description="Sem permissão."),
            404: OpenApiResponse(description="Nada encontrado.")
        },
        examples=[
            OpenApiExample(
                "Exemplo de Retorno com Dados",
                value={
                    "results": [
                        {
                        "id": "357ab638-43c2-425d-b5a9-4f277c39fc84",
                        "precatorio": "3f09ae47-16ef-4c45-ab31-43c53446aaa4",
                        "proponente_nome": "Spatialcaver3",
                        "valor_proposto": "100000.00",
                        "taxa_desconto": "20.00",
                        "taxa_juros_anual": "12.50",
                        "prazo_pagamento_meses": 1,
                        "data_vencimento": "31-12-2026",
                        "observacoes": None,
                        "valor_liquido_cedente": "95000.00",
                        "valor_liquido_proponente": "99013.64",
                        "lucro": "100.00",
                        "status": "RASCUNHO",
                        "created_at": "13-01-2026 11:18",
                        }
                    ]
                },
                response_only=True, 
                status_codes=["200"]
            )
        ]
    ),
    
    build=extend_schema(
        tags=["Propostas"],
    summary="Calculadora Automática de Propostas [ViewSet]",
    description="Calculadora automática de propostas de antecipação de precatórios.",
    responses={
        201: ProposalSerializer,
        400: OpenApiResponse(description="Erro de validação nos dados."),
        401: OpenApiResponse(description="Não autenticado"),
        403: OpenApiResponse(description="Sem permissão."),
    },
    examples=[
        OpenApiExample(
            "Exemplo de Requisição",
            value={
                "precatorio": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                "valor_proposto": "80000.00",
                "taxa_desconto": "20.00",
                "taxa_juros_anual": "12.50",
                "prazo_pagamento_meses": 24,
                "data_vencimento": "2026-12-31",
                "observacoes": "Observação sobre a proposta",
            },
            request_only=True,
        )
    ],
    ),
    
    replace=extend_schema(
        tags=["Propostas"],
        summary="Rota Para Atualizar propostas [ViewSet]",
        request=ProposalSerializer,
        responses={201: ProposalSerializer,
            401: OpenApiResponse(description="Não autenticado"),
            403: OpenApiResponse(description="Sem permissão."),
            404: OpenApiResponse(description="Nada encontrado.")},
        description="Rota para atualização de uma proposta de Antecipação de um precatório, somente Brokers e Administradores podem atualizar propostas.",
        examples=[
            OpenApiExample(
                "Exemplo de Requisição (Brokers e admins)",
                value={
                    "valor_proposto": "100000.00",
                    "taxa_desconto": "20.00",
                    "taxa_juros_anual": "12.50",
                    "prazo_pagamento_meses": 1,
                    "data_vencimento": "31-12-2026",
                    "observacoes": "Atualização de proposta",
                    "status": "ENVIADA",
                },
            )
        ],
    ),
    
    accept=extend_schema(
        tags=["Propostas"],
        summary="Rota para Aceitar proposta [ViewSet]",
        description="Endpoint para aceitar uma proposta. Rejeita automaticamente concorrentes.",
        responses={
            200: ProposalSerializer,
            400: OpenApiResponse(description="O precatório não está mais disponível."),
            401: OpenApiResponse(description="Não autenticado"),
            403: OpenApiResponse(description="Sem permissão."),
            404: OpenApiResponse(description="Nada encontrado.")},
        examples=[
            OpenApiExample(
                "Exemplo de Retorno",
                value={
                    "message": "Proposta aceita e concorrentes rejeitadas com sucesso."
                },
            )
        ],
    ),
    
    drop=extend_schema(
        tags=["Propostas"],
        request=ProposalSerializer,
        summary="Rota para Excluir proposta [ViewSet]",
        description="Rota para exclusão de uma proposta de Antecipação de um precatório, somente Brokers e Administradores podem excluir propostas.",
        responses={201: ProposalSerializer,
            401: OpenApiResponse(description="Não autenticado"),
            403: OpenApiResponse(description="Sem permissão."),
            404: OpenApiResponse(description="Nada encontrado.")},
        examples=[
            OpenApiExample(
                "Exemplo de Retorno",
                value={
                   "message": "Proposta deletada com sucesso!"
                },
            )
        ],      
    )
)

class ProposalCrudViewSet(viewsets.ModelViewSet):
    lookup_field = 'pk'
    serializer_class = ProposalSerializer
    permission_classes = [IsBrokerOrCedenteOrAdmin]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or self.request.user.is_anonymous:
            return Proposal.objects.none()
    
        user = self.request.user
        if user.type_user == "Administrador":
            return Proposal.objects.all()
        elif user.type_user == "Broker":
            return Proposal.objects.filter(proponente=user)
        elif user.type_user == "Cedente":
            return Proposal.objects.filter(precatorio__cedente=user)
        return Proposal.objects.none()

    @action(detail=False, methods=["get"], permission_classes=[IsBrokerOrCedenteOrAdmin], url_path="show")
    def show(self, request, *args, **kwargs):
        user = self.request.user
        try:
            if user.type_user == "Administrador":
                queryset = Proposal.objects.all()
            elif user.type_user == "Broker":
                queryset = Proposal.objects.filter(proponente=user)
            elif user.type_user == "Cedente":
                queryset = Proposal.objects.filter(precatorio__cedente=user)
            serializer = self.serializer_class(queryset, many=True)
            return Response({"results": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=["post"], permission_classes=[IsAdminOrBroker], url_path="build")
    def build(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"result": serializer.data}, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        if getattr(self, "swagger_fake_view", False):
            return None
            
        user = self.request.user
        if user.type_user not in ["Broker", "Administrador"]:
            raise PermissionDenied("Apenas usuários do tipo 'Broker' ou 'Administrador' podem criar propostas.")
        
        with transaction.atomic():
            proposal = serializer.save(proponente=user)
            proposal._current_user = user
            proposal.status = "ENVIADA"
            proposal.save()
    
    @action(detail=True, methods=["put", "patch"], permission_classes=[IsBrokerOrCedenteOrAdmin], url_path="replace")
    def replace(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=["patch"], permission_classes=[IsAdminOrBroker], url_path="accept")
    def accept(self, request, pk=None):
        try:
            ProposalService.aceitar_proposta(pk, request.user)
            return Response({"message": "Proposta aceita e concorrentes rejeitadas."}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=["delete"], permission_classes=[IsAdminOrBroker], url_path="drop")
    def drop(self, request, pk, *args, **kwargs):
        try:
            proposal = get_object_or_404(Proposal, pk=pk)
            proposal.delete()
            return Response(
                {"message": "Proposta deletada com sucesso!"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        