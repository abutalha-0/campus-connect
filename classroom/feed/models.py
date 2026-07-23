from django.db import models
from django.conf import settings

from classroom.classes.models import Classroom


class FeedPost(models.Model):
    """
    A discussion post in a class's feed — a peer space open to every member
    (student or CR) of the class, unrelated to any specific subject. `tag` is
    optional and, when set, must name a subject or faculty member from the
    poster's own class (validated in the serializer).
    """
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.CASCADE,
        related_name='feed_posts'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feed_posts'
    )
    tag = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.classroom.code} → {self.title}"


class FeedVote(models.Model):
    UP = 1
    DOWN = -1
    VALUE_CHOICES = [(UP, 'Up'), (DOWN, 'Down')]

    post = models.ForeignKey(
        FeedPost,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feed_votes'
    )
    value = models.SmallIntegerField(choices=VALUE_CHOICES)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} → {self.post_id} ({self.value})"


class FeedComment(models.Model):
    post = models.ForeignKey(
        FeedPost,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feed_comments'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post_id}"
