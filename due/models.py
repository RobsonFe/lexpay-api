from django.utils import timezone
from django.db import models
from django.conf import settings
from django.db.models import Q 
from uuid import uuid4

from oficio.models import Precatorio
from auth.models import TypeUserChoices 

class DueDiligence(models.Model):

    class StatusAnalise(models.TextChoices):
        PENDENTE = "PENDENTE", "Pendente"
        EM_ANALISE = "EM_ANALISE", "Em Análise"
        APROVADO = "APROVADO", "Aprovado"
        REPACTUADO = "REPACTUADO", "Repactuado"
        REJEITADO = "REJEITADO", "Rejeitado"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    
    precatorio = models.ForeignKey(
        Precatorio, on_delete=models.PROTECT, 
        related_name="diligencias",
        help_text="Precatório que está sendo analisado"
    )
    
    analista = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, 
        limit_choices_to={
            'type_user__in': [
                TypeUserChoices.BROKER,
                TypeUserChoices.ADMINISTRADOR
            ]
        },
        related_name="analises_realizadas",
        help_text="Responsável pela análise (Apenas Admin ou Broker)"
    )

    status_analise = models.CharField(
        max_length=20, choices=StatusAnalise.choices, 
        default=StatusAnalise.PENDENTE,db_index=True
    )
    
    data_inicio_analise = models.DateTimeField(null=True, blank=True)
    data_conclusao_analise = models.DateTimeField(null=True, blank=True)
    
    observacoes = models.TextField(null=True, blank=True)
    documento_aprovado = models.BooleanField(default=False)
    motivo_repactuacao = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'due_diligences'
        verbose_name = 'Due Diligence'
        verbose_name_plural = 'Due Diligences'
        ordering = ['-created_at']
        
        constraints = [
            models.UniqueConstraint(
                fields=['precatorio'], 
                condition=~Q(status_analise='REJEITADO'), 
                name='unique_active_due_diligence'
            )
        ]

    def __str__(self):
        return f"Análise {self.precatorio.numero_processo} - {self.get_status_analise_display()}"
    
    def save(self,*args, **kwargs):
        
        try:
            obj = DueDiligence.objects.get(pk=self.pk)
            if obj.status_analise != self.status_analise:
                if self.status_analise == self.StatusAnalise.EM_ANALISE:
                    self.data_inicio_analise = timezone.now()

                elif self.status_analise in [
                    self.StatusAnalise.APROVADO, 
                    self.StatusAnalise.REJEITADO
                ]: self.data_conclusao_analise = timezone.now()
        except DueDiligence.DoesNotExist:
            ...
        return super().save(*args, **kwargs)
                
