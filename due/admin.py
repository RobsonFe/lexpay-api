from django.contrib import admin

from .models import AnaliseDocumento, DueDiligence


class AnaliseDocumentoInline(admin.TabularInline):
    model = AnaliseDocumento
    extra = 0
    can_delete = False
    readonly_fields = ("documento",)


@admin.register(DueDiligence)
class DueDiligenceAdmin(admin.ModelAdmin):
    list_display = ("id", "precatorio", "analista", "status_analise", "created_at")
    list_filter = ("status_analise",)
    inlines = [AnaliseDocumentoInline]
