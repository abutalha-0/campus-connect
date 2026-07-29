from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import JoinRequest


@receiver(post_save, sender=JoinRequest)
def notify_on_join_request_change(sender, instance, created, update_fields=None, **kwargs):
    from notifications.models import Notification

    # Only react to saves that actually touched status (as our services.py
    # calls do) — avoids re-notifying on unrelated field updates.
    if not created and update_fields is not None and 'status' not in update_fields:
        return

    if created:
        Notification.objects.create(
            recipient=instance.post.author,
            actor=instance.requester,
            notification_type='JOIN_REQUEST',
            post=instance.post,
            join_request=instance,
            message=f'{instance.requester} wants to join "{instance.post.title}"',
        )
        return

    if instance.status in ('ACCEPTED', 'REJECTED'):
        Notification.objects.create(
            recipient=instance.requester,
            actor=instance.reviewed_by,
            notification_type='JOIN_REQUEST_RESPONSE',
            post=instance.post,
            join_request=instance,
            message=f'Your request to join "{instance.post.title}" was {instance.status.lower()}',
        )
