from django.contrib import admin
from due.models import DueDiligence

@admin.register(DueDiligence)
class DueDiligenceAdmin(admin.ModelAdmin):
    list_display = ('analista', 'status_analise', 'data_inicio_analise', 'data_conclusao_analise')
    list_filter = ['status_analise']
    readonly_fields = ('data_inicio_analise', 'data_conclusao_analise', 'created_at', 'updated_at')
    autocomplete_fields = ['precatorio', 'analista']
