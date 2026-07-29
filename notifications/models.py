from django.conf import settings
from django.db import models

from crew.models import JoinRequest, Post


class Notification(models.Model):
    TYPE_CHOICES = [
        ('SYSTEM', 'System'),
        ('JOIN_REQUEST', 'Join request'),
        ('JOIN_REQUEST_RESPONSE', 'Join request response'),
        ('POST_FULL', 'Post full'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notification_actions'
    )
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='SYSTEM')

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    join_request = models.ForeignKey(
        JoinRequest,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )

    message = models.TextField()
    action_url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f'{self.recipient} - {self.notification_type}'
