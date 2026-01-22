from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Proposal, ProposalHistory


@receiver(pre_save, sender=Proposal)
def capture_old_values(sender, instance, **kwargs):

    if instance.pk:
        try:
            old_obj = Proposal.objects.get(pk=instance.pk)
            instance._old_status = old_obj.status
            instance._old_valor = old_obj.valor_proposto
        except Proposal.DoesNotExist:
            instance._old_status = None
            instance._old_valor = None
    else:
        instance._old_status = None
        instance._old_valor = None


@receiver(post_save, sender=Proposal)
def create_history_log(sender, instance, created, **kwargs):
    old_status = getattr(instance, "_old_status", None)
    old_valor = getattr(instance, "_old_valor", None)
    if not created and (
        old_status == instance.status and old_valor == instance.valor_proposto
    ):
        return
    user = getattr(instance, "_current_user", None)
    ProposalHistory.objects.create(
        proposal=instance,
        status_anterior=old_status or "RASCUNHO",
        status_novo=instance.status,
        valor_anterior=old_valor or instance.valor_proposto,
        valor_novo=instance.valor_proposto,
        alterado_por=user,
        motivo_alteracao=getattr(instance, "_change_reason", "Alteração de sistema"),
    )
