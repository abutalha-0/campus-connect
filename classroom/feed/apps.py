from django.apps import AppConfig


class FeedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'classroom.feed'
    label = 'feed'

    def ready(self):
        import classroom.feed.signals
