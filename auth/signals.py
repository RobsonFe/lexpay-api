from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, TypeUserChoices


@receiver(pre_save, sender=User)
def set_administrator_permissions_pre_save(sender, instance, **kwargs):
	"""
	Signal pré-save que automaticamente concede privilégios de administrador
	quando o type_user for 'Administrador'.
	
	Quando um usuário tem type_user = 'Administrador':
	- is_staff = True (pode acessar o Django admin)
	- is_superuser = True (tem todas as permissões)
	
	Este signal é executado ANTES de salvar o usuário, garantindo que
	os privilégios sejam aplicados tanto na criação quanto na atualização.
	"""
	if instance.type_user == TypeUserChoices.ADMINISTRADOR:
		instance.is_staff = True
		instance.is_superuser = True


@receiver(post_save, sender=User)
def verify_administrator_permissions_post_save(sender, instance, created, **kwargs):
	"""
	Signal pós-save que verifica e corrige privilégios de administrador.
	
	Este signal garante que mesmo se houver alguma inconsistência,
	os privilégios sejam mantidos corretos após o salvamento.
	
	Usa update() para evitar loop infinito do signal.
	"""
	if instance.type_user == TypeUserChoices.ADMINISTRADOR:
		needs_update = False
		update_fields = {}
		
		if not instance.is_staff:
			update_fields['is_staff'] = True
			needs_update = True
		
		if not instance.is_superuser:
			update_fields['is_superuser'] = True
			needs_update = True
		
		if needs_update:
			User.objects.filter(pk=instance.pk).update(**update_fields)
