from proposal.serializer import ProposalSerializer, ProposalHistorySerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import    extend_schema
from rest_framework.views import APIView
from rest_framework import status
from proposal.models import Proposal

class CreateProposalView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        request=ProposalSerializer, 
        responses={
            201: ProposalSerializer,
            400: "Bad Request"
        }, 
        tags = ["Proposal"],
       description=
        'Rota para criação de uma proposta de Antecipação de um precatório'
    )
    def post(self, request):
        try:
            serializer = ProposalSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
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
        tags=["Proposal"],
        description="Rota para listagem de propostas de Antecipação de precatórios"
        
    )
    def get(self, request):
        try:
            propopsals = Proposal.objects.all()
            serializer = ProposalSerializer(propopsals, many=True)
            return Response({'message': 'proposals', 'data': serializer.data }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)