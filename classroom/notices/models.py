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
    # blank=True at the DB level only so existing rows (backfilled by
    # migration) and this model stay flexible; the API requires a real title
    # on create (see NoticeSerializer).
    title = models.CharField(max_length=200, blank=True)
    text = models.TextField()
    # Optional highlighted callout label (e.g. "Exam date", "New deadline").
    # Empty means no free-text callout.
    highlight = models.CharField(max_length=200, blank=True)
    # Optional structured event date/time (e.g. an exam or deadline). Either
    # of these being set also triggers the highlighted callout, independent
    # of `highlight` above. event_time is only meaningful when event_date is
    # set. Kept structured (not baked into `highlight` text) so the Schedule
    # feature can read it later.
    event_date = models.DateField(null=True, blank=True)
    event_time = models.TimeField(null=True, blank=True)
    # Optional Cloudinary URL for an attached file.
    attachment_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject.name} → notice by {self.author.username}"
