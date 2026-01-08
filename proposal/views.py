from proposal.serializer import ProposalSerializer, ProposalHistorySerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import    extend_schema
from rest_framework.views import APIView
from rest_framework import status
from proposal.models import Proposal
from django.shortcuts import get_object_or_404 
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError



class CreateProposalView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        tags = ["Propostas"],
        request=ProposalSerializer, 
        responses={
            201: ProposalSerializer,
            400: "Bad Request"
        }, 
       description = 'Rota para criação de uma proposta de Antecipação de um precatório'
    )
    def post(self, request):
        try:
            serializer = ProposalSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Proposal created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
            
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
class ProposalListView(APIView):
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=None, 
        responses={
            200: 'List Of Proposals',
            400: "Bad Request"
        },
        tags=["Propostasl"],
        description="Rota para listagem de propostas de Antecipação de precatórios"
        
    )
    def get(self, request):
        try:
            propopsals = Proposal.objects.all()
            serializer = ProposalSerializer(propopsals, many=True)
            return Response({'message': 'proposals', 'data': serializer.data }, status=status.HTTP_200_OK)
        
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
        description="Rota para atualização de uma proposta de Antecipação de um precatório"
    )
    
    def put(self, request, pk, *args, **kwargs):
        try:
            proposal = get_object_or_404(Proposal, pk=pk)
            serializer = ProposalSerializer(proposal, data=request.data)
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
        responses={200: "{'message': 'Proposta aceita com sucesso'}", 400: "Erro de validação"}
    )
    def post(self, request, pk):
       
        proposal = get_object_or_404(Proposal, pk=pk)
        precatorio = proposal.precatorio

        try:
            with transaction.atomic():
               
                if proposal.data_vencimento < timezone.now().date():
                    proposal.status = 'EXPIRADA'
                    proposal.save()
                    raise ValidationError("Esta proposta está expirada.")

                
                if precatorio.status != 'DISPONIVEL':
                    raise ValidationError("O precatório não está mais disponível para negociação.")


                proposal.status = 'ACEITA'
                proposal.save()

                precatorio.status = 'EM_NEGOCIACAO'
                precatorio.save()

                outras_propostas = Proposal.objects.filter(
                    precatorio=precatorio,
                    status='ENVIADA'
                ).exclude(id=proposal.id)

                outras_propostas.update(status='REJEITADA')

            return Response(
                {"message": "Proposta aceita e concorrentes rejeitadas com sucesso."},
                status=status.HTTP_200_OK
            )

        except ValidationError as e:
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Erro interno ao processar aceite."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)