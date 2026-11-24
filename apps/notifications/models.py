"""Notifications app - in-app + email notifications (shared service).

Notification types cover all three pillars:
  - network: new connection, like, comment, message
  - learning: enrollment, course update, certificate issued, assessment graded
  - careers: application status change, new job match, interview scheduled
  - system: announcements, payment receipts
"""
from django.conf import settings
from django.db import models


class Notification(models.Model):
    """A notification addressed to a single user."""

    NETWORK = 'network'
    LEARNING = 'learning'
    CAREER = 'career'
    PAYMENT = 'payment'
    SYSTEM = 'system'
    CATEGORIES = [
        (NETWORK, 'Network'),
        (LEARNING, 'Learning'),
        (CAREER, 'Career'),
        (PAYMENT, 'Payment'),
        (SYSTEM, 'System'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notifications',
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='actions_notifications',
    )
    category = models.CharField(max_length=20, choices=CATEGORIES, default=SYSTEM)
    verb = models.CharField(max_length=120,
                             help_text='e.g. "liked your post", "applied to your job"')
    target_text = models.CharField(max_length=200, blank=True,
                                    help_text='Display name of the target object')
    target_url = models.URLField(blank=True,
                                  help_text='Clickable link to the target object')

    is_read = models.BooleanField(default=False)
    is_emailed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        actor_name = self.actor.get_full_name() if self.actor else 'System'
        return f'{actor_name} {self.verb} ({self.recipient})'


class Announcement(models.Model):
    """Platform-wide announcements broadcast to all users."""

    title = models.CharField(max_length=200)
    body = models.TextField()
    is_pinned = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='announcements',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title
