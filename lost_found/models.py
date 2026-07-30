from django.db import models
from django.conf import settings


class LostFoundItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('LOST', 'Lost'),
        ('FOUND', 'Found'),
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLAIMED', 'Claimed'),
        ('CLOSED', 'Closed'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lost_found_items'
    )
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    item_type = models.CharField(max_length=5, choices=ITEM_TYPE_CHOICES, default='LOST')
    category = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    image_url = models.URLField(blank=True)
    contact_info = models.CharField(max_length=200, blank=True)
    date_seen = models.DateField(null=True, blank=True)
    found_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.item_type})'
