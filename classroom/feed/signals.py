from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import FeedPost


@receiver(post_save, sender=FeedPost)
def notify_on_feed_post_created(sender, instance, created, **kwargs):
    if not created:
        return

    from classroom.classes.models import ClassMembership
    from notifications.models import Notification

    recipient_ids = ClassMembership.objects.filter(
        classroom=instance.classroom
    ).exclude(student=instance.author).values_list('student_id', flat=True)

    action_url = f'classroom/feed/{instance.id}'
    Notification.objects.bulk_create([
        Notification(
            recipient_id=student_id,
            actor=instance.author,
            notification_type='FEED_POST',
            message=f'New post in your class feed: {instance.title}',
            action_url=action_url,
        )
        for student_id in recipient_ids
    ])
