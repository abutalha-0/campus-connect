from django.apps import AppConfig


class CrewConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crew'
    label = 'crew'

    def ready(self):
        import crew.signals
