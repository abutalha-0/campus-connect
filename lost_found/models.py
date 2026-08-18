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
    item_type = models.CharField(max_length=5, choices=ITEM_TYPE_CHOICES, default='LOST', db_index=True)
    category = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=200, blank=True)
    image_url = models.URLField(blank=True)
    contact_info = models.CharField(max_length=200, blank=True)
    event_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='OPEN', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'item_type']),
        ]

    def __str__(self):
        return f'{self.title} ({self.item_type})'


class ClaimQuestion(models.Model):
    item = models.ForeignKey(LostFoundItem, on_delete=models.CASCADE, related_name='claim_questions')
    question_text = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return f'Question for {self.item.title}: {self.question_text}'


class ClaimAttempt(models.Model):
    STATUS_CHOICES = [('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')]
    item = models.ForeignKey(LostFoundItem, on_delete=models.CASCADE, related_name='claim_attempts')
    claimant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='claim_attempts')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('item', 'claimant')

    def __str__(self):
        return f'Claim attempt by {self.claimant} for {self.item.title} ({self.status})'


class ClaimAnswer(models.Model):
    attempt = models.ForeignKey(ClaimAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(ClaimQuestion, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=255)

    def __str__(self):
        return f'Answer to Q{self.question_id}: {self.answer_text}'

