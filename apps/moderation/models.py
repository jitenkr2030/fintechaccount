"""Moderation app - content moderation queue (Administration & Analytics).

Spec Section 3: "Moderation, Content Management, Employer Management, Reports"

Flagged posts, comments, communities, jobs, users go here for review by
platform administrators. Auto-moderation rules can also queue items.
"""
from django.conf import settings
from django.db import models


class Report(models.Model):
    """A user-reported piece of content."""

    POST = 'post'
    COMMENT = 'comment'
    COMMUNITY = 'community'
    TOPIC = 'topic'
    USER = 'user'
    JOB = 'job'
    COURSE = 'course'
    REVIEW = 'review'
    OTHER = 'other'
    TARGET_TYPES = [
        (POST, 'Post'),
        (COMMENT, 'Comment'),
        (COMMUNITY, 'Community'),
        (TOPIC, 'Community Topic'),
        (USER, 'User'),
        (JOB, 'Job'),
        (COURSE, 'Course'),
        (REVIEW, 'Course Review'),
        (OTHER, 'Other'),
    ]

    SPAM = 'spam'
    HARASSMENT = 'harassment'
    MISINFORMATION = 'misinformation'
    OFFTOPIC = 'offtopic'
    ILLEGAL = 'illegal'
    OTHER = 'other'
    REASONS = [
        (SPAM, 'Spam or scam'),
        (HARASSMENT, 'Harassment or abuse'),
        (MISINFORMATION, 'Misinformation'),
        (OFFTOPIC, 'Off-topic / irrelevant'),
        (ILLEGAL, 'Illegal content'),
        (OTHER, 'Other'),
    ]

    PENDING = 'pending'
    REVIEWING = 'reviewing'
    RESOLVED = 'resolved'
    DISMISSED = 'dismissed'
    STATUSES = [
        (PENDING, 'Pending'),
        (REVIEWING, 'Reviewing'),
        (RESOLVED, 'Resolved'),
        (DISMISSED, 'Dismissed'),
    ]

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='reports_made',
    )
    target_type = models.CharField(max_length=20, choices=TARGET_TYPES)
    target_id = models.PositiveIntegerField()
    target_url = models.URLField(blank=True)
    reason = models.CharField(max_length=30, choices=REASONS)
    description = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUSES, default=PENDING)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reports_assigned',
    )
    resolution_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['status', '-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['target_type', 'target_id']),
        ]

    def __str__(self):
        return f'{self.target_type} #{self.target_id} - {self.reason} ({self.status})'


class ModerationAction(models.Model):
    """An action taken by an admin on a reported item."""

    REMOVE_CONTENT = 'remove_content'
    BAN_USER = 'ban_user'
    WARN_USER = 'warn_user'
    RESTORE = 'restore'
    NO_ACTION = 'no_action'
    ACTIONS = [
        (REMOVE_CONTENT, 'Remove content'),
        (BAN_USER, 'Ban user'),
        (WARN_USER, 'Warn user'),
        (RESTORE, 'Restore content'),
        (NO_ACTION, 'No action'),
    ]

    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='actions')
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                              null=True, related_name='moderation_actions')
    action = models.CharField(max_length=30, choices=ACTIONS)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.admin} {self.action} on {self.report}'
