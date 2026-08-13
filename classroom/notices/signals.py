from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notice


@receiver(post_save, sender=Notice)
def notify_on_notice_posted(sender, instance, created, **kwargs):
    if not created:
        return

    from classroom.classes.models import ClassMembership
    from notifications.models import Notification

    recipient_ids = ClassMembership.objects.filter(
        classroom__subjects=instance.subject
    ).exclude(student=instance.author).values_list('student_id', flat=True)

    # Includes subject_id: SubjectDetailActivity's "jump to notice" deep link
    # needs it, and the notice id alone isn't enough to open that screen.
    action_url = f'classroom/subjects/{instance.subject_id}/notices/{instance.id}'
    title = instance.title or instance.text[:60]
    Notification.objects.bulk_create([
        Notification(
            recipient_id=student_id,
            actor=instance.author,
            notification_type='NOTICE_POSTED',
            message=f'New notice in {instance.subject.name}: {title}',
            action_url=action_url,
        )
        for student_id in recipient_ids
    ])
