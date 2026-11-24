"""Payments app - Razorpay payments for courses, events, memberships (Phase 3+).

Revenue model items handled here:
  - Paid courses (₹499-4,999)
  - Premium professional membership (₹99-299/month)
  - Featured job listings (₹999+)
  - Recruiter subscription (₹2,999/month)
  - Paid events/webinars (sponsorship)
"""
import uuid

from django.conf import settings
from django.db import models


class Order(models.Model):
    """A platform payment order (Razorpay order id is stored)."""

    COURSE = 'course'
    MEMBERSHIP = 'membership'
    EVENT = 'event'
    JOB_FEATURED = 'job_featured'
    RECRUITER_SUB = 'recruiter_sub'
    CORPORATE_TRAINING = 'corporate_training'
    OTHER = 'other'
    CONTENT_TYPES = [
        (COURSE, 'Course'),
        (MEMBERSHIP, 'Premium Membership'),
        (EVENT, 'Event Registration'),
        (JOB_FEATURED, 'Featured Job Listing'),
        (RECRUITER_SUB, 'Recruiter Subscription'),
        (CORPORATE_TRAINING, 'Corporate Training'),
        (OTHER, 'Other'),
    ]

    CREATED = 'created'
    ATTEMPTED = 'attempted'
    PAID = 'paid'
    FAILED = 'failed'
    REFUNDED = 'refunded'
    STATUSES = [
        (CREATED, 'Created'),
        (ATTEMPTED, 'Attempted'),
        (PAID, 'Paid'),
        (FAILED, 'Failed'),
        (REFUNDED, 'Refunded'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name='orders')
    amount = models.DecimalField(max_digits=12, decimal_places=2,
                                  help_text='Amount in INR')
    currency = models.CharField(max_length=8, default='INR')
    content_type_label = models.CharField(max_length=30, choices=CONTENT_TYPES)
    object_id = models.PositiveIntegerField(help_text='ID of the related Course/Event/etc.')
    description = models.CharField(max_length=300, blank=True)

    # Razorpay
    razorpay_order_id = models.CharField(max_length=80, blank=True)
    razorpay_payment_id = models.CharField(max_length=80, blank=True)
    razorpay_signature = models.CharField(max_length=200, blank=True)

    status = models.CharField(max_length=20, choices=STATUSES, default=CREATED)
    reference = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} - {self.amount} {self.currency} ({self.status})'


class Subscription(models.Model):
    """A recurring subscription (premium membership or recruiter)."""

    PREMIUM_MEMBER = 'premium_member'
    RECRUITER = 'recruiter'
    TYPES = [
        (PREMIUM_MEMBER, 'Premium Member'),
        (RECRUITER, 'Recruiter Subscription'),
    ]

    ACTIVE = 'active'
    CANCELLED = 'cancelled'
    EXPIRED = 'expired'
    PAST_DUE = 'past_due'
    STATUSES = [
        (ACTIVE, 'Active'),
        (CANCELLED, 'Cancelled'),
        (EXPIRED, 'Expired'),
        (PAST_DUE, 'Past due'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name='subscriptions')
    subscription_type = models.CharField(max_length=30, choices=TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    billing_cycle_days = models.PositiveIntegerField(default=30)
    status = models.CharField(max_length=20, choices=STATUSES, default=ACTIVE)

    razorpay_subscription_id = models.CharField(max_length=80, blank=True)

    started_at = models.DateTimeField(auto_now_add=True)
    current_period_end = models.DateTimeField()
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.user} {self.subscription_type} ({self.status})'
