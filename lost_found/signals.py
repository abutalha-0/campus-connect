from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ClaimAttempt


@receiver(post_save, sender=ClaimAttempt)
def notify_on_claim_attempt_change(sender, instance, created, update_fields=None, **kwargs):
    from notifications.models import Notification

    if not created and update_fields is not None and 'status' not in update_fields:
        return

    action_url = f'lostfound/items/{instance.item.id}'
    actor_name = getattr(instance.claimant, 'full_name', None) or instance.claimant.username

    if created:
        Notification.objects.create(
            recipient=instance.item.user,
            actor=instance.claimant,
            notification_type='CLAIM_REQUEST',
            lost_found_item=instance.item,
            claim_attempt=instance,
            message=f'{actor_name} submitted a claim request for "{instance.item.title}"',
            action_url=action_url,
        )
        return

    if instance.status == 'APPROVED':
        Notification.objects.create(
            recipient=instance.claimant,
            actor=instance.item.user,
            notification_type='CLAIM_REQUEST_RESPONSE',
            lost_found_item=instance.item,
            claim_attempt=instance,
            message=f'Your claim request for "{instance.item.title}" was accepted! Location and details are now revealed.',
            action_url=action_url,
        )
    elif instance.status == 'REJECTED':
        Notification.objects.create(
            recipient=instance.claimant,
            actor=instance.item.user,
            notification_type='CLAIM_REQUEST_RESPONSE',
            lost_found_item=instance.item,
            claim_attempt=instance,
            message=f'Your claim request for "{instance.item.title}" was rejected.',
            action_url=action_url,
        )
