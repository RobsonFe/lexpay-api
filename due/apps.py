from django.apps import AppConfig


class DueConfig(AppConfig):
    defaul_auto_field = 'django.db.models.BigAuth_field'
    name = 'due'

    def ready(self):
        import due.signal