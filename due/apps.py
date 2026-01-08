from django.apps import AppConfig


class DueConfig(AppConfig):
    defaulf_auto_field = 'django.db.models.BigAutoField'
    name = 'due'

    def ready(self):
        import due.signal