from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import RouteJoinRequest


@receiver(post_save, sender=RouteJoinRequest)
def notify_on_route_join_request_change(sender, instance, created, **kwargs):
    from notifications.models import Notification

    # Unlike crew's JoinRequest, nothing in this app calls .save() with
    # update_fields, and every non-created save here really is a status
    # change (accept/reject, or reopening a rejected/cancelled request back
    # to PENDING) — so branching on status alone is enough, no extra guard.
    action_url = f'routemate/routes/{instance.route.id}'

    if created or instance.status == 'PENDING':
        Notification.objects.create(
            recipient=instance.route.owner,
            actor=instance.requester,
            notification_type='ROUTE_JOIN_REQUEST',
            message=f'{instance.requester} wants to join your route to {instance.route.destination}',
            action_url=action_url,
        )
        return

    if instance.status in ('ACCEPTED', 'REJECTED'):
        Notification.objects.create(
            recipient=instance.requester,
            actor=instance.route.owner,
            notification_type='ROUTE_JOIN_REQUEST_RESPONSE',
            message=f'Your request to join the route to {instance.route.destination} was {instance.status.lower()}',
            action_url=action_url,
        )
