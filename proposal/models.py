from django.db import models
import uuid
from oficio.models import Precatorio
from auth.models import User
# Create your models here.


STATUS = [
    ('RASCUNHO', 'rascunho'),
    ('ENVIADA', 'enviada'),
    ('ACEITA', 'aceita'),
    ('REJEITADA', 'rejeitada'), 
    ('EXPIRADA', 'expirada')
]




#OPTEI POR DEIXAR AS RELAÇÕES COM A CONFIG PROTECT PARA QUE OS DADOS NÃO SEJAM APAGADOS E QUE SE MANTENHA UM REGISTRO DE TODAS AS TRANSAÇÕES. 

class Proposal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    precatorio = models.ForeignKey(Precatorio, on_delete=models.PROTECT, max_length=255)
    proponente = models.ForeignKey(User, on_delete=models.PROTECT, max_length=255)
    valor_proposto = models.DecimalField(max_digits=18, decimal_places=2)
    taxa_desconto = models.DecimalField(max_digits=5, decimal_places=2)
    taxa_juros_anual = models.DecimalField(max_digits=5, decimal_places=2)
    prazo_pagamento_meses = models.IntegerField()
    valor_liquido_cedente = models.DecimalField(max_digits=18, decimal_places=2)
    valor_liquido_proponente = models.DecimalField(max_digits=18, decimal_places=2)
    margem_lucro_percentual = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS, default='RASCUNHO')
    data_vencimento = models.DateField()
    observacoes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    
    
    
    def __str__(self):
        return f"Proposal: {self.id} - {self.status}, Proponente: {self.proponente} Valor: {self.valor_proposto} Vencimento: {self.data_vencimento}"
    
    
    
    
class ProposalHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proposal = models.ForeignKey(Proposal, on_delete=models.PROTECT, max_length=255)
    status_anterior = models.CharField(max_length=20, choices=STATUS, default='RASCUNHO')
    status_novo = models.CharField(max_length=20, choices=STATUS, default='ENVIADA')
    valor_anterior = models.DecimalField(max_digits=18, decimal_places=2, null=False, blank=False)
    valor_novo = models.DecimalField(max_digits=18, decimal_places=2, null=False, blank=False)
    alterado_por = models.ForeignKey(User, on_delete=models.PROTECT, max_length=255)
    motivo_alteracao = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"ProposalHistory: {self.proposal.id} - {self.status_anterior} -> {self.status_novo} alterado por {self.alterado_por} Pelo motivo: {self.motivo_alteracao}"