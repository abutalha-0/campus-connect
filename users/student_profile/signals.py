from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    # Only students get a student Profile. Faculty accounts have their own
    # FacultyProfile, created explicitly during faculty registration.
    if created and instance.role == 'STUDENT':
        Profile.objects.create(user=instance)