from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User, Address


class CustomUserCreationForm(UserCreationForm):
	"""Formulário customizado para criação de usuários no admin"""
	class Meta:
		model = User
		fields = ('email', 'username')


class CustomUserChangeForm(UserChangeForm):
	"""Formulário customizado para edição de usuários no admin"""
	class Meta:
		model = User
		fields = '__all__'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
	"""
	Configuração do admin para o modelo User com suporte a alteração de senha.
	
	Esta classe herda de BaseUserAdmin que já possui funcionalidades nativas
	para alteração de senha no Django admin.
	"""
	form = CustomUserChangeForm
	add_form = CustomUserCreationForm
	
	list_display = ('email', 'username', 'name', 'cpf', 'phone', 'type_user', 'is_active', 'is_staff', 'created_at', 'updated_at')
	list_filter = ('is_active', 'is_staff', 'type_user', 'created_at', 'updated_at')
	search_fields = ('email', 'username', 'name', 'cpf', 'phone')
	readonly_fields = ('created_at', 'updated_at', 'last_login')
	ordering = ('-created_at',)
	
	fieldsets = (
		(None, {'fields': ('email', 'username', 'password')}),
		(_('Informações Pessoais'), {'fields': ('name', 'cpf', 'phone', 'avatar', 'type_user')}),
		(_('Permissões'), {
			'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
		}),
		(_('Datas Importantes'), {'fields': ('last_login', 'created_at', 'updated_at')}),
	)
	
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('email', 'username', 'password1', 'password2'),
		}),
		(_('Informações Pessoais'), {
			'fields': ('name', 'cpf', 'phone', 'type_user'),
		}),
		(_('Permissões'), {
			'fields': ('is_active', 'is_staff', 'is_superuser'),
		}),
	)
	
	filter_horizontal = ('groups', 'user_permissions')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
	"""Configuração do admin para o modelo Address"""
	list_display = ('user', 'address', 'number', 'city', 'state', 'zip_code', 'created_at', 'updated_at')
	list_filter = ('state', 'city', 'created_at', 'updated_at')
	search_fields = ('user__email', 'user__name', 'address', 'city', 'state', 'zip_code')
	readonly_fields = ('created_at', 'updated_at')
	ordering = ('-created_at',)