from django.contrib import admin
from .models import User, Address

admin.site.register(User)
admin.site.register(Address)

class UserAdmin(admin.ModelAdmin):
	list_display = ('email', 'username', 'name', 'cpf', 'phone', 'is_active', 'is_staff', 'created_at', 'updated_at')
	list_filter = ('is_active', 'is_staff', 'created_at', 'updated_at')
	search_fields = ('email', 'username', 'name', 'cpf', 'phone')
	readonly_fields = ('created_at', 'updated_at')
	ordering = ('-created_at',)