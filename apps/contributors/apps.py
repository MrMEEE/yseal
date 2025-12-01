from django.apps import AppConfig


class ContributorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.contributors'
    verbose_name = 'Contributors'
    
    def ready(self):
        import apps.contributors.signals
