import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DueDiligence, AnaliseDocumento
from oficio.models import StatusPrecatorioChoices

logger = logging.getLogger(__name__)

@receiver(post_save, sender=DueDiligence)
def criar_analises_automaticas(sender, instance, created, **kwargs):
    """
        Gatilho de evento: Quando o evento disparado pelo Sender(Due...) com um save(post_save) o @receiver 'escuta' que houve uma alteração, o created é um booleano e verifica se foi um update(False) ou created (True) e faz a mudança de estado do Precatório.
    """ 
    if created:
        docs = instance.precatorio.documentos.all()
        lista_docs = []

        for doc in docs:
            item = AnaliseDocumento(
                due_diligence = instance,
                documento = doc,
                status = AnaliseDocumento.StatusDocumento.PENDENTE
            )
            lista_docs.append(item)
        AnaliseDocumento.objects.bulk_create(lista_docs)
        if lista_docs:
            logger.info(f"criado para a Due {instance.id}")
        else:
            logger.warning(f"Due {instance.id} criada, mas o Precatório não tem documentos cadastrados.")
        return
    
    precatorio = instance.precatorio

    if instance.status_analise == DueDiligence.StatusAnalise.APROVADO:
        if precatorio.status != StatusPrecatorioChoices.DISPONIVEL:
            precatorio.status = StatusPrecatorioChoices.DISPONIVEL
            precatorio.save()

        logger.info(f"Precatório: {precatorio.numero_processo} - Liberação para venda via DueDilligence: {instance.id}")  
    
    elif instance.status_analise == DueDiligence.StatusAnalise.REJEITADO:
        if precatorio.status != StatusPrecatorioChoices.SUSPENSO:
            precatorio.status = StatusPrecatorioChoices.SUSPENSO 
            precatorio.save()
            logger.info(f"Precatório {precatorio.numero_processo} suspenso por falha na Due Diligence {instance.id}.")
    
    elif instance.status_analise == DueDiligence.StatusAnalise.REPACTUADO:
        if precatorio.status != StatusPrecatorioChoices.ANALISE:
            precatorio.status = StatusPrecatorioChoices.ANALISE
            precatorio.save()
            logger.info(f"Precatório {precatorio.numero_processo} enviado para correção via Due Diligence.")