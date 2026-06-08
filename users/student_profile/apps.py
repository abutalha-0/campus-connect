from django.apps import AppConfig


class StudentProfileConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users.student_profile'
    label = 'student_profile'

    def ready(self):
        import users.student_profile.signals