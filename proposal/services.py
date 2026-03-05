from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError
from oficio.models import StatusPrecatorioChoices
from .models import Proposal
from proposal.serializer import ProposalSerializer
from rest_framework.response import Response
from rest_framework import generics, status, viewsets
from django.shortcuts import get_object_or_404
from django.db import transaction
from auth.models import User


class ProposalService:
    @staticmethod
    def aceitar_proposta(proposal_id, user_name):
        proposal = (
            Proposal.objects.select_related("precatorio")
            .select_for_update()
            .get(pk=proposal_id)
        )
        precatorio = proposal.precatorio

        with transaction.atomic():
            if proposal.data_vencimento < timezone.now().date():
                proposal.status = "EXPIRADA"
                proposal.save()
                raise ValidationError("Esta proposta está expirada.")

            if precatorio.status != StatusPrecatorioChoices.DISPONIVEL:
                raise ValidationError("O precatório não está mais disponível.")

            proposal._current_user = user_name
            proposal._change_reason = "Aceite processado via Service Layer"

            proposal.status = "ACEITA"
            proposal.save()

            precatorio.status = StatusPrecatorioChoices.NEGOCIACAO
            precatorio.save()

            Proposal.objects.filter(precatorio=precatorio, status="ENVIADA").exclude(
                id=proposal.id
            ).update(status="REJEITADA")
            
            return proposal
        

    @staticmethod
    def listar_propostas(user):
        queryset = Proposal.objects.select_related("precatorio", "proponente")
        
        if user.type_user == "Administrador":
            return queryset.all()
        elif user.type_user == "Broker":
            return queryset.filter(proponente=user)
        elif user.type_user == "Cedente":
            return queryset.filter(precatorio__cedente=user)
        
        return Proposal.objects.none()
    
    @staticmethod
    def criar_propostas(user, data, request):
        user = request.user
        
        try:
            with transaction.atomic():
                proposal = Proposal.objects.create(proponente=user, **data)
                proposal._current_user = user
                proposal.status = "ENVIADA"
                proposal.save()
                return proposal
        except Exception as e:
            raise ValidationError(f"Erro ao criar proposta: {str(e)}")
    @staticmethod
    def deletar_propostas(proposal_id):
        try:
            with transaction.atomic():
                proposal = Proposal.objects.get(pk=proposal_id)
                proposal.delete()
        except Exception as e:
            raise ValidationError(f"Erro ao deletar proposta: {str(e)}")
        
    @staticmethod
    def atualizar_proposta(proposal_id, data, user):
        try:
            proposal = Proposal.objects.select_related("precatorio", "proponente").get(pk=proposal_id)
            if user.type_user not in ["Administrador", "Broker"]:
                raise PermissionDenied("Sem permissão para alterar esta proposta.")
            
            for key, value in data.items():
                if hasattr(proposal, key):
                    if key == 'precatorio':
                        setattr(proposal, 'precatorio_id', value)
                    else:
                        setattr(proposal, key, value)
                proposal.save()
                return proposal
        except Proposal.DoesNotExist:
            raise ValidationError("Proposta não encontrada.")
        