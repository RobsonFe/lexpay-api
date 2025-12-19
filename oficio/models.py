from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import uuid
import os
from auth.models import TypeUserChoices 

class EsferaChoices:
    FEDERAL = 'Federal'
    ESTADUAL = 'Estadual'
    MUNICIPAL = 'Municipal'
    
    CHOICES = [
        (FEDERAL, 'Federal'),
        (ESTADUAL, 'Estadual'),
        (MUNICIPAL, 'Municipal'),
    ]

class NaturezaChoices:
    ALIMENTAR = 'Alimentar'
    COMUM = 'Comum'
    
    CHOICES = [
        (ALIMENTAR, 'Alimentar'),
        (COMUM, 'Comum'),
    ]

class StatusPrecatorioChoices:
    ANALISE = 'Em Análise'
    DISPONIVEL = 'Disponível'
    NEGOCIACAO = 'Em Negociação'
    VENDIDO = 'Vendido'
    SUSPENSO = 'Suspenso'
    
    CHOICES = [
        (ANALISE, 'Em Análise'),
        (DISPONIVEL, 'Disponível'),
        (NEGOCIACAO, 'Em Negociação'),
        (VENDIDO, 'Vendido'),
        (SUSPENSO, 'Suspenso'),
    ]

class Tribunal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=150, unique=True, help_text="Ex: Tribunal Regional Federal da 1ª Região")
    sigla = models.CharField(max_length=20, unique=True, help_text="Ex: TRF1")
    uf = models.CharField(max_length=2, help_text="Estado do tribunal", null=True, blank=True)
    
    class Meta:
        db_table = 'tribunais'
        verbose_name = 'Tribunal'
        verbose_name_plural = 'Tribunais'
        ordering = ['sigla']

    def __str__(self):
        return self.sigla

class EnteDevedor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255, help_text="Ex: Fazenda Pública do Estado de São Paulo")
    cnpj = models.CharField(max_length=20, unique=True, null=True, blank=True)
    esfera = models.CharField(max_length=20, choices=EsferaChoices.CHOICES)
    
    class Meta:
        db_table = 'entes_devedores'
        verbose_name = 'Ente Devedor'
        verbose_name_plural = 'Entes Devedores'

    def __str__(self):
        return f"{self.nome} ({self.esfera})"

class Precatorio(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    cedente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='precatorios_cedente',
        limit_choices_to={'type_user': TypeUserChoices.CEDENTE},
        help_text="O dono original do título"
    )
    advogado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='precatorios_advogado',
        limit_choices_to={'type_user': TypeUserChoices.ADVOGADO}
    )
    tribunal = models.ForeignKey(Tribunal, on_delete=models.PROTECT)
    ente_devedor = models.ForeignKey(EnteDevedor, on_delete=models.PROTECT)
    numero_processo = models.CharField(max_length=50, unique=True, help_text="Número CNJ ou do Ofício Requisitório")
    natureza = models.CharField(max_length=20, choices=NaturezaChoices.CHOICES)
    valor_principal = models.DecimalField(max_digits=18, decimal_places=2, help_text="Valor de face do precatório")
    valor_venda = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True, help_text="Valor pretendido para venda")
    percentual_honorarios = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Percentual de honorários contratuais destacadados")
    data_expedicao = models.DateField(help_text="Data de expedição do ofício")
    ano_orcamentario = models.IntegerField(help_text="Ano do orçamento para pagamento")
    status = models.CharField(
        max_length=20, 
        choices=StatusPrecatorioChoices.CHOICES, 
        default=StatusPrecatorioChoices.ANALISE
    )
    descricao = models.TextField(null=True, blank=True, help_text="Observações gerais sobre o ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'precatorios'
        verbose_name = 'Precatório'
        verbose_name_plural = 'Precatórios'
        indexes = [
            models.Index(fields=['numero_processo']),
            models.Index(fields=['status']),
            models.Index(fields=['natureza']),
            models.Index(fields=['ano_orcamentario']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.numero_processo} - {self.get_status_display()}"

def validate_file_extension(value):
	"""
	Valida se o arquivo tem extensão permitida (PDF ou Word).
	"""
	ext = os.path.splitext(value.name)[1].lower()
	allowed_extensions = ['.pdf', '.doc', '.docx']
	if ext not in allowed_extensions:
		raise ValidationError(
			_('Formato de arquivo não permitido. Apenas arquivos PDF (.pdf) e Word (.doc, .docx) são aceitos.')
		)

def validate_file_size(value):
	"""
	Valida o tamanho máximo do arquivo (10MB).
	"""
	max_size = 10 * 1024 * 1024
	if value.size > max_size:
		raise ValidationError(
			_('O arquivo é muito grande. Tamanho máximo permitido: 10MB.')
		)

class Documento(models.Model):
	"""
	Tabela para armazenar os documentos (PDFs e Word) relacionados aos precatórios.
	Suporta: Ofício Requisitório, Memória de Cálculo, Contrato Social, etc.
	"""
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	precatorio = models.ForeignKey(Precatorio, on_delete=models.CASCADE, related_name='documentos')
	titulo = models.CharField(max_length=100, help_text="Ex: Ofício Requisitório, Memória de Cálculo")
	arquivo = models.FileField(
		upload_to='precatorios/docs/%Y/%m/',
		validators=[validate_file_extension, validate_file_size],
		help_text="Apenas arquivos PDF (.pdf) e Word (.doc, .docx) são aceitos. Tamanho máximo: 10MB"
	)
	enviado_em = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'precatorios_documentos'
		verbose_name = 'Documento'
		verbose_name_plural = 'Documentos'
		ordering = ['-enviado_em']

	def __str__(self):
		return f"{self.titulo} - {self.precatorio.numero_processo}"

	def get_file_extension(self):
		"""
		Retorna a extensão do arquivo.
		"""
		if self.arquivo:
			return os.path.splitext(self.arquivo.name)[1].lower()
		return None

	def get_file_size_mb(self):
		"""
		Retorna o tamanho do arquivo em MB.
		"""
		if self.arquivo:
			return round(self.arquivo.size / (1024 * 1024), 2)
		return None

	def is_pdf(self):
		"""
		Verifica se o arquivo é um PDF.
		"""
		return self.get_file_extension() == '.pdf'

	def is_word(self):
		"""
		Verifica se o arquivo é um documento Word.
		"""
		return self.get_file_extension() in ['.doc', '.docx']