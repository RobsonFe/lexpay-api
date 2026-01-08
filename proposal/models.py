from django.db import models
import uuid
from oficio.models import Precatorio
from auth.models import User
from decimal import Decimal
from due.models import DueDiligence
# Create your models here.


class StausChoices:
    
    RASCUNHO = 'Rascunho'
    ENVIADA = 'Enviada'
    ACEITA = 'Aceita'
    REJEITADA = 'Rejeitada'
    EXPIRADA = 'Expirada'

    STATUS = [
        ('RASCUNHO', 'rascunho'),
        ('ENVIADA', 'enviada'),
        ('ACEITA', 'aceita'),
        ('REJEITADA', 'rejeitada'), 
        ('EXPIRADA', 'expirada')
    ]






class Proposal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    precatorio = models.ForeignKey(Precatorio, on_delete=models.PROTECT)
    proponente = models.ForeignKey(User, on_delete=models.PROTECT, limit_choices_to={'type_user': 'Broker'})
    valor_proposto = models.DecimalField(max_digits=18, decimal_places=2)
    taxa_desconto = models.DecimalField(max_digits=5, decimal_places=2)
    taxa_juros_anual = models.DecimalField(max_digits=5, decimal_places=2)
    prazo_pagamento_meses = models.IntegerField()
    valor_liquido_cedente = models.DecimalField(max_digits=18, decimal_places=2)
    valor_liquido_proponente = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(max_length=20, choices=StausChoices.STATUS, default='RASCUNHO')
    data_vencimento = models.DateField()
    observacoes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    _current_user = None
    
    
    @property
    def margem_lucro_percentual(self):
        if self.valor_proposto > 0:
            valor_face = self.precatorio.valor_principal
            
            return ((valor_face - self.valor_proposto) / self.valor_proposto) * Decimal('100')
        
        return 0
    
    def __str__(self):
        return f"Proposal: {self.id} - {self.status}, Proponente: {self.proponente} Valor: {self.valor_proposto} Vencimento: {self.data_vencimento}"
    

    def validate(self):
        diligencia_aprovada = DueDiligence.objects.filter(
        precatorio=self.precatorio, 
        status_analise='APROVADO' 
    ).exists()


        if self.precatorio.status != 'Disponível' or not diligencia_aprovada:
            raise ValueError("O precatório não está disponível ou não possui Due Diligence aprovada.")

        if self.valor_proposto <= 0:
            raise ValueError("O valor proposto deve ser maior que zero.")
        if self.taxa_desconto < 0 or self.taxa_desconto > 100:
            raise ValueError("A taxa de desconto deve estar entre 0 e 100.")
        if self.taxa_juros_anual < 0 or self.taxa_juros_anual > 100:
            raise ValueError("A taxa de juros anual deve estar entre 0 e 100.")
        if self.prazo_pagamento_meses <= 0:
            raise ValueError("O prazo de pagamento em meses deve ser maior que zero.")
        if self.taxa_desconto + self.taxa_juros_anual > 100:
            raise ValueError("A soma das taxas de desconto e juros anual deve ser menor ou igual a 100.")

    def save(self, *args, **kwargs):
        # 1. Buscando dados do relacionamento (Precatorio)
        
        valor_face_precatorio = self.precatorio.valor_principal
        percentual_honorarios_precatorio = self.precatorio.percentual_honorarios
        
        self.validate()
        
        # CÁLCULO CEDENTE

        honorarios = self.valor_proposto * (percentual_honorarios_precatorio / 100)
        
        # O resultado final salvo no campo do model   
        self.valor_liquido_cedente = self.valor_proposto - honorarios
       
        
        
         # CÁLCULO PROPONENTE
        if self.prazo_pagamento_meses > 0:
            
        # Fórmula: M = C * (1 + i)^t

            base_juros = Decimal('1') + (self.taxa_juros_anual / Decimal('100'))
            fator_tempo = base_juros ** (self.prazo_pagamento_meses / Decimal('12'))
            valor_final = self.valor_proposto * fator_tempo
            custo_juros = valor_final - self.valor_proposto
            self.valor_liquido_proponente = valor_face_precatorio - self.valor_proposto - custo_juros
        else:
            self.valor_liquido_proponente = valor_face_precatorio - self.valor_proposto
             
        # MARGEM DE LUCRO

        if self.valor_proposto > 0:
            self.margem_lucro_percentual = ((valor_face_precatorio - self.valor_proposto) / self.valor_proposto) * Decimal('100')
            
        super().save(*args, **kwargs)
        
        
        
        

class ProposalHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    status_anterior = models.CharField(max_length=20, choices=StausChoices.STATUS, default='RASCUNHO')
    status_novo = models.CharField(max_length=20, choices=StausChoices.STATUS, default='ENVIADA')
    valor_anterior = models.DecimalField(max_digits=18, decimal_places=2, null=False, blank=False)
    valor_novo = models.DecimalField(max_digits=18, decimal_places=2, null=False, blank=False)
    alterado_por = models.ForeignKey(User, on_delete=models.PROTECT)
    motivo_alteracao = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"ProposalHistory: {self.proposal.id} - {self.status_anterior} -> {self.status_novo} alterado por {self.alterado_por} Pelo motivo: {self.motivo_alteracao}"