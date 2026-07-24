from django.conf import settings
from django.db import models

from .validators import validate_post_details


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.CharField(max_length=300, blank=True)
    icon = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('OPEN', 'Open'),
        ('FULL', 'Full'),
        ('CLOSED', 'Closed'),
        ('EXPIRED', 'Expired'),
        ('CANCELLED', 'Cancelled'),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='crew_posts'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='posts'
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN')
    description = models.TextField()
    location = models.CharField(max_length=120, blank=True)
    contact_info = models.CharField(max_length=200, blank=True)

    # Category-specific fields (course code, contest tech stack, travel budget, etc.)
    # live here instead of one column per category. See crew/validators.py for
    # the per-category schema each category's details must satisfy.
    details = models.JSONField(default=dict, blank=True)

    skills = models.ManyToManyField(
        'student_profile.Skill',
        blank=True,
        related_name='crew_posts'
    )

    max_members = models.PositiveIntegerField(null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['category', 'status']),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        super().clean()
        validate_post_details(self.category.slug, self.details)

    @property
    def accepted_members_count(self):
        return self.members.count()

    @property
    def is_full(self):
        if self.max_members is None:
            return False
        return self.accepted_members_count >= self.max_members


class JoinRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='join_requests')
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='join_requests'
    )
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_join_requests'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('post', 'requester')

    def __str__(self):
        return f'{self.requester} -> {self.post}'


class PostMember(models.Model):
    """An accepted member of a post. Created when a JoinRequest is accepted
    (see crew/services.py). Lets us compute capacity without recounting
    JoinRequest rows on every read.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='crew_memberships'
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f'{self.user} member of {self.post}'


class Bookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='crew_bookmarks'
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'post')

    def __str__(self):
        return f'{self.user} bookmarked {self.post}'
