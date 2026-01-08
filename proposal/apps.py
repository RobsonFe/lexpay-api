from django.apps import AppConfig



class ProposalConfig(AppConfig):
    name = 'proposal'
    default_auto_field = 'django.db.models.BigAutoField'
    
    def ready(self):
        import proposal.signals