from django.db import models
from django.conf import settings


class FacultyProfile(models.Model):
    DESIGNATION_CHOICES = [
        ('LECTURER', 'Lecturer'),
        ('ASSISTANT_PROFESSOR', 'Assistant Professor'),
        ('ASSOCIATE_PROFESSOR', 'Associate Professor'),
        ('PROFESSOR', 'Professor'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='faculty_profile'
    )
    employee_id = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100)
    designation = models.CharField(
        max_length=30,
        choices=DESIGNATION_CHOICES,
        default='ASSISTANT_PROFESSOR'
    )
    # Faculty must be approved by the admin office before they can
    # create classes or subjects.
    is_verified = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Faculty Profile of {self.user.username}"
