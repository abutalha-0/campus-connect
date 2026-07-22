import secrets

from django.db import models
from django.conf import settings

from classroom.subjects.models import Subject

# Uppercase letters + digits, excluding easily-confused characters (I, O, 0, 1).
CLASS_CODE_ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'


class Classroom(models.Model):
    # One class per creator ("one class at a time").
    creator = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_class'
    )
    # Shareable code students use to join the class.
    code = models.CharField(max_length=6, unique=True)
    # Courses added by their subject secret codes.
    subjects = models.ManyToManyField(
        Subject,
        related_name='classes',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Class {self.code} by {self.creator.username}"

    @classmethod
    def generate_unique_code(cls):
        while True:
            code = ''.join(secrets.choice(CLASS_CODE_ALPHABET) for _ in range(6))
            if not cls.objects.filter(code=code).exists():
                return code
