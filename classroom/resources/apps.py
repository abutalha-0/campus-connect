from django.apps import AppConfig


class ResourcesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'classroom.resources'
    label = 'resources'

    def ready(self):
        import classroom.resources.signals
