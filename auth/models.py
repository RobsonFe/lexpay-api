from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import uuid


class UserManager(BaseUserManager):

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório')
        if not username:
            raise ValueError('O username é obrigatório')
        if not password:
            raise ValueError('A senha é obrigatória')

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.is_active = extra_fields.get('is_active', True)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser deve ter is_superuser=True.')

        return self.create_user(email, username, password, **extra_fields)
    

class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'auth_app.User',
        on_delete=models.CASCADE,
        help_text="Usuário do endereço",
        related_name="addresses"
    )
    address = models.CharField(
        max_length=255,
        help_text="Endereço do usuário",
        null=True,
        blank=True
    )
    number = models.CharField(
        max_length=10,
        help_text="Número do endereço",
        null=True,
        blank=True
    )
    complement = models.CharField(
        max_length=255,
        help_text="Complemento do endereço",
        null=True,
        blank=True
    )
    city = models.CharField(
        max_length=255,
        help_text="Cidade do endereço",
        null=True,
        blank=True
    )
    state = models.CharField(
        max_length=2,
        help_text="Estado do endereço",
        null=True,
        blank=True
    )
    zip_code = models.CharField(max_length=10, help_text="CEP do endereço", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, help_text="Data de criação")
    updated_at = models.DateTimeField(auto_now=True, help_text="Data de atualização")

    class Meta:
        db_table = 'addresses'
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'
        indexes = [
            models.Index(fields=['city']),
            models.Index(fields=['state']),
            models.Index(fields=['zip_code']),
        ]

    def __str__(self):
        return f"{self.user.name} - {self.address}, {self.number} - {self.city}/{self.state}"


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/default.png',
        help_text="Avatar do usuário",
        null=True,
        blank=True
    )
    username = models.CharField(
        max_length=100,
        unique=True,
        help_text="Username do usuário",
        null=False,
        blank=False
    )
    name = models.CharField(
        max_length=100,
        help_text="Nome completo do usuário",
        null=True,
        blank=True
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
        help_text="Email do usuário",
        null=False,
        blank=False
    )
    cpf = models.CharField(
        max_length=11,
        unique=True,
        help_text="CPF do usuário",
        null=True,
        blank=True
    )
    phone = models.CharField(
        max_length=11,
        unique=True,
        help_text="Telefone do usuário",
        null=True,
        blank=True
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Designa se este usuário deve ser tratado como ativo."
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Designa se o usuário pode acessar o site de administração."
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Data de criação")
    updated_at = models.DateTimeField(auto_now=True, help_text="Data de atualização")

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.name or self.username} - {self.cpf}"

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    class Meta:
        db_table = 'users'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['cpf']),
            models.Index(fields=['phone']),
        ]
        ordering = ['-created_at']