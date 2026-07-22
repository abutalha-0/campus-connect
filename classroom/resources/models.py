from django.db import models

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
    # Free-text grouping label, e.g. "WEEK 1 · INTRODUCTION". Resources are
    # grouped by this value in the UI.
    topic = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=3, choices=RESOURCE_TYPES)
    # Human-readable size/length, e.g. "240 KB" or "42 min".
    size_label = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    # Cloudinary URL for uploaded documents, or an external link for videos.
    file_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Oldest first so topics render in creation order (WEEK 1, WEEK 2, …).
        ordering = ['created_at']

    def __str__(self):
        return f"{self.subject.name} → {self.title}"
