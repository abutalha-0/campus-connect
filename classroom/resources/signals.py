from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Resource


@receiver(post_save, sender=Resource)
def notify_on_resource_posted(sender, instance, created, **kwargs):
    if not created:
        return

    from classroom.classes.models import ClassMembership
    from notifications.models import Notification

    recipients_qs = ClassMembership.objects.filter(classroom__subjects=instance.subject)
    if instance.author_id:
        recipients_qs = recipients_qs.exclude(student_id=instance.author_id)
    recipient_ids = recipients_qs.values_list('student_id', flat=True)

    action_url = f'classroom/resources/{instance.id}'
    Notification.objects.bulk_create([
        Notification(
            recipient_id=student_id,
            actor_id=instance.author_id,
            notification_type='RESOURCE_POSTED',
            message=f'New resource in {instance.subject.name}: {instance.title}',
            action_url=action_url,
        )
        for student_id in recipient_ids
    ])
