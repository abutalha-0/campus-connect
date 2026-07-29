from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import FacultyProfile


@receiver(post_save, sender=FacultyProfile)
def sync_user_role_to_faculty(sender, instance, **kwargs):
    # A FacultyProfile should never exist for a non-FACULTY user (e.g. one
    # attached by mistake through the Django admin, which doesn't check
    # this). Keep User.role in sync so login/routing always agrees with
    # which profile actually exists.
    user = instance.user
    if user.role != 'FACULTY':
        user.role = 'FACULTY'
        user.save(update_fields=['role'])
