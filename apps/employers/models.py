"""Employers app - company profiles (Pillar C spec).

Implements the "For employers" module: company profiles, post vacancies,
search candidate profiles, shortlist, schedule interviews, manage recruitment,
verify submitted credentials with appropriate consent.
"""
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class EmployerProfile(models.Model):
    """A company / recruiter profile. One-to-one with the user (employer role)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='employer_profile',
    )
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    company_name = models.CharField(max_length=200)
    tagline = models.CharField(max_length=200, blank=True)
    about = models.TextField(blank=True)

    logo = models.ImageField(upload_to='employer_logos/', null=True, blank=True)
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)

    # Industry & size
    industry = models.CharField(max_length=100, blank=True,
                                 help_text='e.g. Accounting, Banking, FinTech')
    company_size = models.CharField(max_length=40, blank=True,
                                     help_text='e.g. 11-50, 51-200, 201-1000')

    # Location
    headquarters_city = models.CharField(max_length=100, blank=True)
    headquarters_state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=80, default='India')

    # Contact
    contact_name = models.CharField(max_length=120, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)

    # Verification
    is_verified = models.BooleanField(default=False,
                                       help_text='Verified company / recruiter')
    verification_notes = models.TextField(blank=True)

    # Stats (denormalised)
    jobs_count = models.PositiveIntegerField(default=0)
    hires_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_verified', 'company_name']

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.company_name)[:140] or 'employer'
            candidate = base
            i = 2
            while EmployerProfile.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f'{base}-{i}'
                i += 1
            self.slug = candidate
        super().save(*args, **kwargs)


class Interview(models.Model):
    """An interview slot scheduled by an employer for an applicant."""

    SCHEDULED = 'scheduled'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    RESCHEDULED = 'rescheduled'
    STATUSES = [
        (SCHEDULED, 'Scheduled'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
        (RESCHEDULED, 'Rescheduled'),
    ]

    application = models.ForeignKey(
        'applications.JobApplication', on_delete=models.CASCADE,
        related_name='interviews',
    )
    interviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='interviews_conducted',
    )
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    location = models.CharField(max_length=200, blank=True,
                                 help_text='Address or meeting URL')
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default=SCHEDULED)
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scheduled_at']

    def __str__(self):
        return f'Interview: {self.application} at {self.scheduled_at}'
