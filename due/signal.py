import logging

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from oficio.models import Precatorio, StatusPrecatorioChoices

from .models import AnaliseDocumento, DueDiligence

logger = logging.getLogger(__name__)


@receiver(post_save, sender=DueDiligence)
def criar_analises_automaticas(sender, instance, created, **kwargs):
    """
    Gerencia criação de checklist e atualização de status do Precatório com segurança.
    """
    if created:
        docs = instance.precatorio.documentos.all()
        lista_docs = []

        for doc in docs:
            item = AnaliseDocumento(
                due_diligence=instance,
                documento=doc,
                status=AnaliseDocumento.StatusDocumento.PENDENTE,
            )
            lista_docs.append(item)
        AnaliseDocumento.objects.bulk_create(lista_docs)
        if lista_docs:
            logger.info(f"criado para a Due {instance.id}")
        else:
            logger.warning(
                f"Due {instance.id} criada, mas o Precatório não tem documentos cadastrados."
            )
        return

    with transaction.atomic():
        try:
            precatorio = Precatorio.objects.select_for_update().get(
                id=instance.precatorio_id
            )

            if instance.status_analise == DueDiligence.StatusAnalise.APROVADO:
                if precatorio.status != StatusPrecatorioChoices.DISPONIVEL:
                    precatorio.status = StatusPrecatorioChoices.DISPONIVEL
                    precatorio.save()
                    logger.info(
                        f"Precatório: {precatorio.numero_processo} - Liberação para venda via DueDiligence: {instance.id}"
                    )

            elif instance.status_analise == DueDiligence.StatusAnalise.REJEITADO:
                if precatorio.status != StatusPrecatorioChoices.SUSPENSO:
                    precatorio.status = StatusPrecatorioChoices.SUSPENSO
                    precatorio.save()
                    logger.info(
                        f"Precatório {precatorio.numero_processo} suspenso por falha na Due Diligence {instance.id}."
                    )

            elif instance.status_analise == DueDiligence.StatusAnalise.REPACTUADO:
                if precatorio.status != StatusPrecatorioChoices.ANALISE:
                    precatorio.status = StatusPrecatorioChoices.ANALISE
                    precatorio.save()
                    logger.info(
                        f"Precatório {precatorio.numero_processo} enviado para correção via Due Diligence."
                    )

        except Precatorio.DoesNotExist:
            logger.error(
                f"Error: O precatório de id {instance.precatorio_id} não pode ser atualizado pois ele não existe."
            )
