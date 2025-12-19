from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from .models import Tribunal, EnteDevedor, Precatorio, Documento


@admin.register(Tribunal)
class TribunalAdmin(admin.ModelAdmin):
	"""
	Configuração do admin para o modelo Tribunal.
	
	Gerencia os tribunais onde os precatórios são expedidos.
	"""
	list_display = ('sigla', 'nome', 'uf', 'get_precatorios_count')
	list_filter = ('uf',)
	search_fields = ('sigla', 'nome', 'uf')
	ordering = ('sigla',)
	
	fieldsets = (
		(_('Informações Básicas'), {
			'fields': ('sigla', 'nome', 'uf')
		}),
	)
	
	def get_precatorios_count(self, obj):
		"""
		Retorna a quantidade de precatórios associados a este tribunal.
		"""
		count = obj.precatorio_set.count()
		if count > 0:
			url = reverse('admin:oficio_precatorio_changelist')
			return format_html(
				'<a href="{}?tribunal__id__exact={}">{} precatórios</a>',
				url,
				obj.id,
				count
			)
		return '0 precatórios'
	
	get_precatorios_count.short_description = 'Precatórios'
	get_precatorios_count.admin_order_field = 'precatorio_set__count'


@admin.register(EnteDevedor)
class EnteDevedorAdmin(admin.ModelAdmin):
	"""
	Configuração do admin para o modelo EnteDevedor.
	
	Gerencia os entes devedores (órgãos públicos) que devem os precatórios.
	"""
	list_display = ('nome', 'cnpj', 'esfera', 'get_precatorios_count')
	list_filter = ('esfera',)
	search_fields = ('nome', 'cnpj', 'esfera')
	ordering = ('nome',)
	
	fieldsets = (
		(_('Informações Básicas'), {
			'fields': ('nome', 'cnpj', 'esfera')
		}),
	)
	
	def get_precatorios_count(self, obj):
		"""
		Retorna a quantidade de precatórios associados a este ente devedor.
		"""
		count = obj.precatorio_set.count()
		if count > 0:
			url = reverse('admin:oficio_precatorio_changelist')
			return format_html(
				'<a href="{}?ente_devedor__id__exact={}">{} precatórios</a>',
				url,
				obj.id,
				count
			)
		return '0 precatórios'
	
	get_precatorios_count.short_description = 'Precatórios'
	get_precatorios_count.admin_order_field = 'precatorio_set__count'


class DocumentoInline(admin.TabularInline):
	"""
	Inline para gerenciar documentos dentro do admin de Precatório.
	
	Permite adicionar, editar e visualizar documentos diretamente
	na página de edição do precatório.
	"""
	model = Documento
	extra = 0
	fields = ('titulo', 'arquivo', 'enviado_em', 'get_file_info')
	readonly_fields = ('enviado_em', 'get_file_info')
	
	def get_file_info(self, obj):
		"""
		Exibe informações sobre o arquivo (extensão e tamanho).
		"""
		if obj.pk and obj.arquivo:
			extension = obj.get_file_extension()
			size_mb = obj.get_file_size_mb()
			return format_html(
				'<strong>{}</strong><br><small>{} MB</small>',
				extension.upper() if extension else 'N/A',
				size_mb if size_mb else '0'
			)
		return '-'
	
	get_file_info.short_description = 'Informações do Arquivo'


@admin.register(Precatorio)
class PrecatorioAdmin(admin.ModelAdmin):
	"""
	Configuração do admin para o modelo Precatorio.
	
	Gerencia os precatórios com todas as funcionalidades necessárias
	para visualização, filtragem, busca e edição.
	"""
	list_display = (
		'numero_processo',
		'get_cedente_name',
		'tribunal',
		'ente_devedor',
		'valor_principal',
		'valor_venda',
		'status',
		'natureza',
		'ano_orcamentario',
		'created_at',
		'get_documentos_count'
	)
	
	list_filter = (
		'status',
		'natureza',
		'ano_orcamentario',
		'tribunal',
		'ente_devedor',
		'created_at',
		'updated_at'
	)
	
	search_fields = (
		'numero_processo',
		'cedente__name',
		'cedente__email',
		'advogado__name',
		'advogado__email',
		'descricao',
		'tribunal__sigla',
		'tribunal__nome',
		'ente_devedor__nome'
	)
	
	readonly_fields = (
		'id',
		'created_at',
		'updated_at',
		'get_documentos_list'
	)
	
	ordering = ('-created_at',)
	
	fieldsets = (
		(_('Informações Básicas'), {
			'fields': ('numero_processo', 'status', 'natureza', 'descricao')
		}),
		(_('Valores'), {
			'fields': (
				'valor_principal',
				'valor_venda',
				'percentual_honorarios'
			)
		}),
		(_('Relacionamentos'), {
			'fields': ('cedente', 'advogado', 'tribunal', 'ente_devedor')
		}),
		(_('Datas'), {
			'fields': ('data_expedicao', 'ano_orcamentario')
		}),
		(_('Documentos'), {
			'fields': ('get_documentos_list',),
			'classes': ('collapse',)
		}),
		(_('Informações do Sistema'), {
			'fields': ('id', 'created_at', 'updated_at'),
			'classes': ('collapse',)
		}),
	)
	
	inlines = [DocumentoInline]
	
	filter_horizontal = ()
	
	def get_cedente_name(self, obj):
		"""
		Retorna o nome do cedente com link para o admin do usuário.
		"""
		if obj.cedente:
			url = reverse('admin:auth_app_user_change', args=[obj.cedente.pk])
			return format_html(
				'<a href="{}">{}</a>',
				url,
				obj.cedente.name or obj.cedente.email
			)
		return '-'
	
	get_cedente_name.short_description = 'Cedente'
	get_cedente_name.admin_order_field = 'cedente__name'
	
	def get_documentos_count(self, obj):
		"""
		Retorna a quantidade de documentos associados ao precatório.
		"""
		if obj.pk:
			count = obj.documentos.count()
			if count > 0:
				return format_html(
					'<strong>{}</strong> documento(s)',
					count
				)
		return '0 documentos'
	
	get_documentos_count.short_description = 'Documentos'
	
	def get_documentos_list(self, obj):
		"""
		Exibe lista de documentos do precatório na página de edição.
		"""
		if obj.pk:
			documentos = obj.documentos.all()
			if documentos:
				html = '<ul>'
				for doc in documentos:
					url = reverse('admin:oficio_documento_change', args=[doc.pk])
					extension = doc.get_file_extension() or 'N/A'
					size_mb = doc.get_file_size_mb() or 0
					html += format_html(
						'<li><a href="{}"><strong>{}</strong></a> - {} ({:.2f} MB)</li>',
						url,
						doc.titulo,
						extension.upper(),
						size_mb
					)
				html += '</ul>'
				return format_html(html)
		return 'Nenhum documento cadastrado'
	
	get_documentos_list.short_description = 'Lista de Documentos'
	
	def get_queryset(self, request):
		"""
		Otimiza as queries usando select_related e prefetch_related.
		"""
		qs = super().get_queryset(request)
		return qs.select_related(
			'cedente',
			'advogado',
			'tribunal',
			'ente_devedor'
		).prefetch_related('documentos')


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
	"""
	Configuração do admin para o modelo Documento.
	
	Gerencia os documentos (PDFs e Word) associados aos precatórios.
	"""
	list_display = (
		'titulo',
		'get_precatorio_link',
		'get_file_type',
		'get_file_size_display',
		'enviado_em'
	)
	
	list_filter = ('enviado_em',)
	
	search_fields = (
		'titulo',
		'precatorio__numero_processo',
		'arquivo'
	)
	
	readonly_fields = (
		'id',
		'enviado_em',
		'get_file_type',
		'get_file_size_display',
		'get_file_preview'
	)
	
	ordering = ('-enviado_em',)
	
	fieldsets = (
		(_('Informações Básicas'), {
			'fields': ('precatorio', 'titulo', 'arquivo')
		}),
		(_('Informações do Arquivo'), {
			'fields': (
				'get_file_type',
				'get_file_size_display',
				'get_file_preview'
			)
		}),
		(_('Informações do Sistema'), {
			'fields': ('id', 'enviado_em'),
			'classes': ('collapse',)
		}),
	)
	
	def get_precatorio_link(self, obj):
		"""
		Retorna link para o precatório relacionado.
		"""
		if obj.precatorio:
			url = reverse('admin:oficio_precatorio_change', args=[obj.precatorio.pk])
			return format_html(
				'<a href="{}">{}</a>',
				url,
				obj.precatorio.numero_processo
			)
		return '-'
	
	get_precatorio_link.short_description = 'Precatório'
	get_precatorio_link.admin_order_field = 'precatorio__numero_processo'
	
	def get_file_type(self, obj):
		"""
		Retorna o tipo do arquivo (PDF ou Word).
		"""
		if obj.arquivo:
			extension = obj.get_file_extension()
			if extension:
				if obj.is_pdf():
					return format_html(
						'<span style="color: #d32f2f; font-weight: bold;">PDF</span>'
					)
				elif obj.is_word():
					return format_html(
						'<span style="color: #1976d2; font-weight: bold;">WORD</span>'
					)
				return extension.upper()
		return '-'
	
	get_file_type.short_description = 'Tipo de Arquivo'
	
	def get_file_size_display(self, obj):
		"""
		Retorna o tamanho do arquivo formatado.
		"""
		if obj.arquivo:
			size_mb = obj.get_file_size_mb()
			if size_mb:
				return format_html('{:.2f} MB', size_mb)
		return '-'
	
	get_file_size_display.short_description = 'Tamanho'
	
	def get_file_preview(self, obj):
		"""
		Exibe link para visualizar/download do arquivo.
		"""
		if obj.arquivo:
			return format_html(
				'<a href="{}" target="_blank" class="button">Abrir Arquivo</a>',
				obj.arquivo.url
			)
		return '-'
	
	get_file_preview.short_description = 'Visualizar Arquivo'
	
	def get_queryset(self, request):
		"""
		Otimiza as queries usando select_related.
		"""
		qs = super().get_queryset(request)
		return qs.select_related('precatorio')
