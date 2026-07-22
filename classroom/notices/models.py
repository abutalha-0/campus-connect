from django.db import models
from django.conf import settings

from classroom.subjects.models import Subject


class Notice(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='notices'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notices'
    )
    text = models.TextField()
    # Optional highlighted callout (e.g. a deadline). Empty means no callout.
    highlight = models.CharField(max_length=200, blank=True)
    # Optional Cloudinary URL for an attached file.
    attachment_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject.name} → notice by {self.author.username}"
