"""Careers app - jobs, job categories, job alerts (Pillar C spec).

Career categories per spec section 2 (Pillar C):
  Accountant, Senior Accountant, GST Executive, Tax Consultant,
  Accounts Manager, Financial Analyst, Audit Assistant,
  Banking Executive, FinTech Developer, Financial Modelling Analyst,
  Tally Operator, CFO / Finance Controller.

For job seekers: search jobs, internships, freelance projects, remote/WFH,
freelance accounting projects, track applications, job alerts.

For employers: post vacancies, search candidate profiles, shortlist, schedule
interviews, recruitment management, verify credentials with consent.
"""
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


# ---------------------------------------------------------------------------
# Job Category
# ---------------------------------------------------------------------------
class JobCategory(models.Model):
    """A pre-seeded job category from the spec."""

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'job categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# Job
# ---------------------------------------------------------------------------
class Job(models.Model):
    """A job / internship / freelance posting."""

    FULL_TIME = 'full_time'
    PART_TIME = 'part_time'
    CONTRACT = 'contract'
    INTERNSHIP = 'internship'
    FREELANCE = 'freelance'
    EMPLOYMENT_TYPES = [
        (FULL_TIME, 'Full-time'),
        (PART_TIME, 'Part-time'),
        (CONTRACT, 'Contract'),
        (INTERNSHIP, 'Internship'),
        (FREELANCE, 'Freelance'),
    ]

    DRAFT = 'draft'
    OPEN = 'open'
    CLOSED = 'closed'
    FILLED = 'filled'
    STATUSES = [
        (DRAFT, 'Draft'),
        (OPEN, 'Open'),
        (CLOSED, 'Closed'),
        (FILLED, 'Filled'),
    ]

    EXPERIENCE_LEVELS = [
        ('entry', 'Entry level (0-2 yrs)'),
        ('mid', 'Mid level (3-7 yrs)'),
        ('senior', 'Senior (8-15 yrs)'),
        ('leadership', 'Leadership (15+ yrs)'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)

    employer = models.ForeignKey(
        'employers.EmployerProfile', on_delete=models.CASCADE,
        related_name='jobs', null=True, blank=True,
    )
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='jobs_posted',
    )

    # Classification
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True,
                                  related_name='jobs')
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default=FULL_TIME)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default='entry')

    # Location
    location_city = models.CharField(max_length=100, blank=True)
    location_state = models.CharField(max_length=100, blank=True)
    is_remote = models.BooleanField(default=False)
    is_wfh = models.BooleanField(default=False, help_text='Work from home allowed')

    # Compensation
    salary_min = models.PositiveIntegerField(default=0, help_text='Per annum INR')
    salary_max = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=8, default='INR')
    is_salary_disclosed = models.BooleanField(default=True)

    # Skills (free text + link to skills later)
    skills_required = models.CharField(max_length=400, blank=True,
                                        help_text='Comma-separated skills')

    # Lifecycle
    status = models.CharField(max_length=20, choices=STATUSES, default=DRAFT)
    openings = models.PositiveIntegerField(default=1)
    application_deadline = models.DateTimeField(null=True, blank=True)

    # Stats
    views_count = models.PositiveIntegerField(default=0)
    applications_count = models.PositiveIntegerField(default=0)

    # Monetisation: featured listings (revenue ₹999+)
    is_featured = models.BooleanField(default=False)
    featured_until = models.DateTimeField(null=True, blank=True)

    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-posted_at']
        indexes = [
            models.Index(fields=['status', '-posted_at']),
            models.Index(fields=['employment_type']),
            models.Index(fields=['is_remote']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:220] or 'job'
            candidate = base
            i = 2
            while Job.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f'{base}-{i}'
                i += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        if self.status != self.OPEN:
            return False
        if self.application_deadline and self.application_deadline < timezone.now():
            return False
        return True

    @property
    def salary_range(self):
        if not self.is_salary_disclosed:
            return 'Not disclosed'
        if self.salary_min and self.salary_max:
            return f'₹{self.salary_min:,} - ₹{self.salary_max:,} / year'
        if self.salary_max:
            return f'Up to ₹{self.salary_max:,} / year'
        if self.salary_min:
            return f'₹{self.salary_min:,}+ / year'
        return 'Competitive'


# ---------------------------------------------------------------------------
# Job Alert
# ---------------------------------------------------------------------------
class JobAlert(models.Model):
    """A saved job search that emails the user when matching jobs are posted."""

    DAILY = 'daily'
    WEEKLY = 'weekly'
    INSTANT = 'instant'
    FREQUENCIES = [
        (DAILY, 'Daily'),
        (WEEKLY, 'Weekly'),
        (INSTANT, 'Instant'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name='job_alerts')
    keywords = models.CharField(max_length=200, blank=True)
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, blank=True)
    location_city = models.CharField(max_length=100, blank=True)
    is_remote = models.BooleanField(null=True, blank=True)
    employment_type = models.CharField(max_length=20, choices=Job.EMPLOYMENT_TYPES, blank=True)
    min_salary = models.PositiveIntegerField(default=0)

    frequency = models.CharField(max_length=20, choices=FREQUENCIES, default=DAILY)
    is_active = models.BooleanField(default=True)
    last_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user}: {self.keywords or self.category or "any"} alert'

    def matches(self, job):
        if self.keywords and self.keywords.lower() not in job.title.lower() \
                and self.keywords.lower() not in job.description.lower():
            return False
        if self.category and job.category_id != self.category_id:
            return False
        if self.location_city and self.location_city.lower() not in job.location_city.lower():
            return False
        if self.is_remote is not None and job.is_remote != self.is_remote:
            return False
        if self.employment_type and job.employment_type != self.employment_type:
            return False
        if self.min_salary and job.salary_max and job.salary_max < self.min_salary:
            return False
        return True
