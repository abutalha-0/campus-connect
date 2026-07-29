from django.apps import AppConfig


class FacultyProfileConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users.faculty_profile'
    label = 'faculty_profile'

    def ready(self):
        import users.faculty_profile.signals
