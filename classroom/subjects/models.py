import secrets

from django.db import models

from users.faculty_profile.models import FacultyProfile


class Subject(models.Model):
    faculty = models.ForeignKey(
        FacultyProfile,
        on_delete=models.CASCADE,
        related_name='subjects'
    )
    name = models.CharField(max_length=200)
    intake = models.CharField(max_length=20)
    section = models.CharField(max_length=20)
    room = models.CharField(max_length=20, blank=True)
    # A short, unique code shared with class creators so they can attach this
    # subject to their class. Generated server-side, never client-supplied.
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.code})"

    @classmethod
    def generate_unique_code(cls):
        """Return a 6-digit numeric code not already used by another subject."""
        while True:
            code = ''.join(secrets.choice('0123456789') for _ in range(6))
            if not cls.objects.filter(code=code).exists():
                return code
