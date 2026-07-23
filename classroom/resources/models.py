from django.db import models
from django.conf import settings

from classroom.subjects.models import Subject


class Resource(models.Model):
    RESOURCE_TYPES = [
        ('PDF', 'PDF'),
        ('PPT', 'Slides'),
        ('DOC', 'Doc'),
        ('VID', 'Video'),
    ]

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='resources'
    )
    # Who posted this — the subject's faculty, or a class CR. Used to enforce
    # "edit/delete your own" (faculty may also moderate).
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posted_resources',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=3, choices=RESOURCE_TYPES)
    description = models.TextField(blank=True)
    # Cloudinary URL for uploaded documents, or an external link for videos.
    file_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Newest first. Resources are grouped by the Saturday–Friday week of
        # their upload time (created_at) on the client.
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject.name} → {self.title}"
