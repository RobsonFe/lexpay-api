from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from oficio.models import StatusPrecatorioChoices
from .models import Proposal


class ProposalService:
    @staticmethod
    def aceitar_proposta(proposal_id, user_name):
        proposal = Proposal.objects.select_related('precatorio').select_for_update().get(pk=proposal_id)
        precatorio = proposal.precatorio
        
        with transaction.atomic():
            if proposal.data_vencimento < timezone.now().date():
                proposal.status = 'EXPIRADA'
                proposal.save()
                raise ValidationError("Esta proposta está expirada.")

            if precatorio.status != StatusPrecatorioChoices.DISPONIVEL:
                raise ValidationError("O precatório não está mais disponível.")

            
            proposal._current_user = user_name
            proposal._change_reason = "Aceite processado via Service Layer"

            
            proposal.status = 'ACEITA'
            proposal.save()

            precatorio.status = StatusPrecatorioChoices.NEGOCIACAO
            precatorio.save()

            
            Proposal.objects.filter(
                precatorio=precatorio,
                status='ENVIADA'
            ).exclude(id=proposal.id).update(status='REJEITADA')

        return proposal