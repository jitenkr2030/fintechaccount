"""Profiles app - extended professional profile data.

Splits the professional identity into structured sections that go beyond the
basic User fields: education, work experience, skills, certifications and a
portfolio of projects/achievements. Together with the User model from the
accounts app these implement the spec's "Professional Profiles" module
(Pillar A).
"""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


# ---------------------------------------------------------------------------
# Skills (shared pick-list)
# ---------------------------------------------------------------------------
class Skill(models.Model):
    """A normalised skill, e.g. 'GST', 'Tally Prime', 'Financial Modelling'."""

    name = models.CharField(max_length=80, unique=True)
    category = models.CharField(max_length=40, blank=True,
                                help_text='e.g. Accounting, Taxation, FinTech, Software')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# Extended profile
# ---------------------------------------------------------------------------
class Profile(models.Model):
    """Extended profile - one per user.

    Holds structured professional data that does not fit on the User model
    (education, experience, etc. live in their own related models below).
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )

    # Public-facing slug
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    # Career summary
    years_experience = models.PositiveIntegerField(default=0)
    current_title = models.CharField(max_length=120, blank=True)
    current_company = models.CharField(max_length=120, blank=True)
    industry = models.CharField(max_length=80, blank=True,
                               help_text='e.g. Accounting, Banking, FinTech, Manufacturing')

    # Social
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    github = models.URLField(blank=True)

    # CV / resume
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)

    # Preferences
    is_open_to_work = models.BooleanField(_('open to work'), default=True)
    is_open_to_mentor = models.BooleanField(_('open to mentoring'), default=False)
    is_open_to_speaking = models.BooleanField(_('open to speaking'), default=False)

    # Verification
    is_verified_professional = models.BooleanField(default=False)
    verification_notes = models.TextField(blank=True)

    # Stats (denormalised for fast display)
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    posts_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Profile: {self.user}'

    @property
    def completion_pct(self):
        """Profile completeness score used on the dashboard."""
        fields = [
            self.user.headline, self.user.bio, self.user.city,
            self.current_title, self.current_company, self.industry,
            self.user.avatar, self.linkedin,
        ]
        filled = sum(1 for f in fields if f)
        related = 0
        if self.experiences.exists():
            related += 1
        if self.educations.exists():
            related += 1
        if self.skills.exists():
            related += 1
        total = len(fields) + 3
        return int(((filled + related) / total) * 100)


# ---------------------------------------------------------------------------
# Profile sections
# ---------------------------------------------------------------------------
class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=120, help_text='e.g. B.Com, CA, MBA')
    field_of_study = models.CharField(max_length=120, blank=True)
    start_year = models.PositiveIntegerField(null=True, blank=True)
    end_year = models.PositiveIntegerField(null=True, blank=True)
    grade = models.CharField(max_length=40, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-end_year', '-start_year']

    def __str__(self):
        return f'{self.degree} @ {self.institution}'


class Experience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='experiences')
    title = models.CharField(max_length=120)
    company = models.CharField(max_length=120)
    employment_type = models.CharField(max_length=40, blank=True,
                                       help_text='Full-time, Part-time, Contract, Internship')
    location = models.CharField(max_length=120, blank=True)
    is_current = models.BooleanField(default=False)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f'{self.title} @ {self.company}'


class Certification(models.Model):
    """A professional certification or qualification the user holds.

    Per spec: certificates must clearly state whether they are platform-issued
    course-completion certificates or qualifications from an authorised
    awarding body. ``is_statutory`` flags statutory qualifications (CA, CMA,
    CS, CPA, etc.).
    """

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=200, help_text='e.g. CA, CMA, CS, CPA, GST Practitioner')
    issuing_body = models.CharField(max_length=200, help_text='e.g. ICAI, ICMAI, ICSI')
    is_statutory = models.BooleanField(
        default=False,
        help_text='Statutory qualification from an authorised awarding body '
                  '(CA/CMA/CS/CPA). If False, this is a course-completion certificate.',
    )
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    credential_id = models.CharField(max_length=120, blank=True)
    credential_url = models.URLField(blank=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f'{self.name} ({self.issuing_body})'


class ProfileSkill(models.Model):
    """Through-model linking a profile/user to a Skill with a proficiency."""

    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'
    EXPERT = 'expert'
    LEVELS = [
        (BEGINNER, 'Beginner'),
        (INTERMEDIATE, 'Intermediate'),
        (ADVANCED, 'Advanced'),
        (EXPERT, 'Expert'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='profiles')
    level = models.CharField(max_length=20, choices=LEVELS, default=INTERMEDIATE)

    class Meta:
        unique_together = [('profile', 'skill')]
        ordering = ['-level']

    def __str__(self):
        return f'{self.profile.user} - {self.skill} ({self.level})'


class PortfolioItem(models.Model):
    """A project, achievement or work sample the user wants to showcase."""

    PROJECT = 'project'
    ACHIEVEMENT = 'achievement'
    PUBLICATION = 'publication'
    OTHER = 'other'
    TYPES = [
        (PROJECT, 'Project'),
        (ACHIEVEMENT, 'Achievement'),
        (PUBLICATION, 'Publication'),
        (OTHER, 'Other'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='portfolio_items')
    title = models.CharField(max_length=200)
    item_type = models.CharField(max_length=20, choices=TYPES, default=PROJECT)
    description = models.TextField()
    url = models.URLField(blank=True)
    image = models.ImageField(upload_to='portfolio/', null=True, blank=True)
    completed_at = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-completed_at']

    def __str__(self):
        return self.title
