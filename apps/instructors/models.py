"""Instructors app - instructor profiles & dashboards (Pillar B spec).

Instructor profile is the public-facing profile of an instructor; it links to
their courses (in the courses app) and to payouts (revenue share model:
instructor commission 15-25%).
"""
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class InstructorProfile(models.Model):
    """Extended profile for users with the instructor role.

    Linked to courses via ``courses`` (related_name='courses_taught' on the
    Course model). Stat fields are denormalised for fast display.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='instructor_profile',
    )
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    # Headline & bio
    title = models.CharField(max_length=200, help_text='e.g. Senior CA, ex-Big 4 Auditor')
    bio = models.TextField()

    # Credentials
    expertise = models.CharField(max_length=300,
                                 help_text='Comma-separated areas, e.g. GST, IFRS, FinTech')
    years_teaching = models.PositiveIntegerField(default=0)
    certifications = models.TextField(blank=True,
                                       help_text='Comma-separated statutory qualifications (CA/CMA/CS/...)')

    # Social
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    youtube = models.URLField(blank=True)

    # Stats (denormalised)
    courses_count = models.PositiveIntegerField(default=0)
    students_count = models.PositiveIntegerField(default=0)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Verification
    is_verified = models.BooleanField(default=False)

    # Revenue share (default 70% instructor / 30% platform; spec says 15-25%
    # commission so the default platform commission is 25%)
    commission_pct = models.DecimalField(max_digits=5, decimal_places=2, default=75.00,
                                          help_text='Instructor share of course revenue (default 75%, platform takes 25%)')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_verified', '-students_count']

    def __str__(self):
        return f'Instructor: {self.user}'

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.user.get_full_name() or self.user.email)[:140]
            candidate = base or 'instructor'
            i = 2
            while InstructorProfile.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f'{base}-{i}'
                i += 1
            self.slug = candidate
        super().save(*args, **kwargs)


class Payout(models.Model):
    """A revenue payout to an instructor."""

    PENDING = 'pending'
    APPROVED = 'approved'
    PAID = 'paid'
    CANCELLED = 'cancelled'
    STATUSES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (PAID, 'Paid'),
        (CANCELLED, 'Cancelled'),
    ]

    instructor = models.ForeignKey(InstructorProfile, on_delete=models.CASCADE,
                                     related_name='payouts')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    period_start = models.DateField()
    period_end = models.DateField()
    status = models.CharField(max_length=20, choices=STATUSES, default=PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)
    reference = models.CharField(max_length=120, blank=True,
                                  help_text='Bank / UPI transaction reference')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.instructor}: {self.amount} ({self.status})'
