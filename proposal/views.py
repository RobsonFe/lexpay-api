from proposal.serializer import ProposalSerializer
from rest_framework.permissions import  IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import    extend_schema, OpenApiExample
from rest_framework.views import APIView
from rest_framework import status, generics
from proposal.models import Proposal
from django.shortcuts import get_object_or_404
from django.db import transaction
from proposal.services import ProposalService
from rest_framework.exceptions import ValidationError, PermissionDenied

class CreateProposalView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer

    @extend_schema(
        tags=["Propostas"],
        summary="Calculadora Automática de Propostas",
        description="Endpoint que valida o status do precatório e Due Diligence aprovada, gerando cálculos financeiros automáticos.",
        request=ProposalSerializer,
        responses={201: ProposalSerializer, 400: "Erro de Validação"},
        examples=[
            OpenApiExample(
                'Exemplo de Requisição (Broker)',
                value={
                    "precatorio": "d290f1ee-6c54-4b01-90e6-d701748f0851",
                    "valor_proposto": "80000.00",
                    "taxa_desconto": "20.00",
                    "taxa_juros_anual": "12.50",
                    "prazo_pagamento_meses": 24,
                    "data_vencimento": "31-12-2026",
                    "observacoes": "Observação sobre a proposta"
                }
            )
        ]
    )
    def perform_create(self, serializer):
        user = self.request.user
        if user.type_user not in ['Broker', 'Admin']:
            raise PermissionDenied("Apenas usuários do tipo 'Broker' podem criar propostas de compra.")
        try:
            with transaction.atomic():
                proposal = serializer.save(proponente=user)
                proposal._current_user = user
                proposal.status = "ENVIADA"
                proposal.save()
                return Response({
                    "result": serializer.data
                }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "error": [str(e)]
            }, status=status.HTTP_400_BAD_REQUEST)

class ProposalListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProposalSerializer
    @extend_schema(
        request=None,
        responses={
            200: 'List Of Proposals',
            400: "Bad Request"
        },
        tags=["Propostas"],
        description="Rota para listagem de propostas de Antecipação de precatórios de acordo com o usuário logado",
        examples=[
            OpenApiExample(
                'Exemplo de Retorno',
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
                            "created_at": "13-01-2026 11:18"
                        }
                    ]
                }
            )
        ]
    )
    def get(self, request):
        user = self.request.user
        try:
            if user.type_user == 'Administrador':
                queryset = Proposal.objects.all()
            elif user.type_user == 'Broker':
                queryset = Proposal.objects.filter(proponente=user)
            elif user.type_user == 'Cedente':
                queryset = Proposal.objects.filter(precatorio__cedente=user)
            serializer = self.serializer_class(queryset, many=True)
            return Response({'results': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)






class ProposalUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        tags=["Propostas"],
        request=ProposalSerializer,
        responses={
            200: ProposalSerializer,
            400: "Bad Request"
        },
        description="Rota para atualização de uma proposta de Antecipação de um precatório",
        examples=[
            OpenApiExample(
                'Exemplo de Requisição (Brokers e admins)',
                value={
                        "valor_proposto": "100000.00",
                        "taxa_desconto": "20.00",
                        "taxa_juros_anual": "12.50",
                        "prazo_pagamento_meses": 1,
                        "data_vencimento": "31-12-2026",
                        "observacoes": "Atualização de proposta",
                        "status": "ENVIADA",
                }
            )
        ]
    )
    def patch(self, request, pk, *args, **kwargs):
        try:
            proposal = get_object_or_404(Proposal, pk=pk)
            serializer = ProposalSerializer(proposal, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Proposta atualizada com sucesso!', 'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProposalDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        tags=["Propostas"],
        request=ProposalSerializer,
        responses={
            200: ProposalSerializer,
            400: "Bad Request"
        },
        description="Rota para atualização de uma proposta de Antecipação de um precatório"
    )
    def delete(self, request, pk, *args, **kwargs):
        try:
            proposal = get_object_or_404(Proposal, pk=pk)
            proposal.delete()
            return Response({'message': 'Proposta deletada com sucesso!'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProposalAcceptView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Propostas"],
        description="Endpoint para aceitar uma proposta. Rejeita automaticamente concorrentes.",
        responses={200: "{'message': 'Proposta aceita com sucesso'}", 400: "Erro de validação"},
        examples=[
            OpenApiExample(
                'Exemplo de Retorno',
                value={
                    "message": "Proposta aceita e concorrentes rejeitadas com sucesso."
                }
            )
        ]
    )


    def patch(self, request, pk):
        try:
            ProposalService.aceitar_proposta(pk, request.user)
            return Response(
                {"message": "Proposta aceita e concorrentes rejeitadas."},
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Erro crítico: {str(e)}"}, status=500)


class InvestorOpportunitiesView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Propostas"],
        description="Lista oportunidades de investimento ordenadas por inteligência de rentabilidade (Score)."
    )
    def get(self, request):

        proposals = Proposal.objects.filter(status='ENVIADA').com_score_atratividade()

        serializer = ProposalSerializer(proposals, many=True)
        return Response({
            "count": proposals.count(),
            "results": serializer.data
        }, status=status.HTTP_200_OK)