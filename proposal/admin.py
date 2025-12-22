from django.contrib import admin
from proposal.models import Proposal, ProposalHistory

# Register your models here.

class ProposalAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'proponente', 'valor_proposto', 'data_vencimento')
    list_filter = ('status', 'data_vencimento', 'proponente')
    search_fields = ('id', 'proponente__username')



admin.site.register(Proposal)



class ProposalHistoryAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'status_anterior', 'status_novo', 'alterado_por', 'motivo_alteracao')
    list_filter = ('proposal', 'status_anterior', 'status_novo')
    search_fields = ('proposal__id', 'alterado_por__username')

admin.site.register(ProposalHistory)