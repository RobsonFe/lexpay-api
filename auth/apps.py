from django.apps import AppConfig


class AuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth'
    label = 'auth_app'
    
    def ready(self):
        """
        Método chamado quando o app está pronto.
        Importa os signals para que sejam registrados automaticamente.
        """
        import auth.signals
