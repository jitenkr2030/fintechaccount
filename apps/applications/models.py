"""Applications app - job applications and tracking (Pillar C spec).

Implements: apply for jobs/internships/freelance, track applications,
shortlist applicants, schedule interviews, recruitment management.

Credential verification with consent is implemented as a flag on the
application - the applicant must opt in to credential verification before
the employer can request verification.
"""
from django.conf import settings
from django.db import models


class JobApplication(models.Model):
    """A user's application to a job."""

    SUBMITTED = 'submitted'
    UNDER_REVIEW = 'under_review'
    SHORTLISTED = 'shortlisted'
    INTERVIEW_SCHEDULED = 'interview_scheduled'
    OFFERED = 'offered'
    REJECTED = 'rejected'
    WITHDRAWN = 'withdrawn'
    HIRED = 'hired'
    STATUSES = [
        (SUBMITTED, 'Submitted'),
        (UNDER_REVIEW, 'Under Review'),
        (SHORTLISTED, 'Shortlisted'),
        (INTERVIEW_SCHEDULED, 'Interview Scheduled'),
        (OFFERED, 'Offered'),
        (REJECTED, 'Rejected'),
        (WITHDRAWN, 'Withdrawn'),
        (HIRED, 'Hired'),
    ]

    job = models.ForeignKey('careers.Job', on_delete=models.CASCADE,
                             related_name='applications')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='job_applications')

    # Application content
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to='applications/resumes/', null=True, blank=True,
                              help_text='Use the profile resume if not provided')
    expected_salary = models.PositiveIntegerField(default=0,
                                                    help_text='Annual INR expectation')
    notice_period_days = models.PositiveIntegerField(default=0)

    # Tracking
    status = models.CharField(max_length=30, choices=STATUSES, default=SUBMITTED)
    employer_notes = models.TextField(blank=True)
    rating = models.PositiveIntegerField(default=0,
                                          help_text='Internal rating 1-5')

    # Consent for credential verification
    consent_verify_credentials = models.BooleanField(
        default=False,
        help_text='Applicant consents to employer verifying their submitted '
                  'qualifications and certifications with the issuing bodies.',
    )

    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('job', 'applicant')]
        ordering = ['-applied_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['applied_at']),
        ]

    def __str__(self):
        return f'{self.applicant} -> {self.job.title}'

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            from apps.careers.models import Job
            Job.objects.filter(pk=self.job_id).update(
                applications_count=models.F('applications_count') + 1,
            )

    def delete(self, *args, **kwargs):
        from apps.careers.models import Job
        Job.objects.filter(pk=self.job_id).update(
            applications_count=models.F('applications_count') - 1,
        )
        super().delete(*args, **kwargs)
