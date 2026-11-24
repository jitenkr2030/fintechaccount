"""Certificates app - course completion certificates (Pillar B spec).

CRITICAL SPEC RULE: Certificates must clearly state whether they are
platform-issued course-completion certificates or qualifications from an
authorised awarding body. NEVER imply CA, CMA, CS or other statutory
qualifications.

Every Certificate issued here is a platform-issued course-completion
certificate. Statutory qualifications are stored on the user's profile via
the ``profiles.Certification`` model with ``is_statutory=True``.
"""
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Certificate(models.Model):
    """A platform-issued course-completion certificate.

    Generated automatically when a student completes a course. Each
    certificate has a unique, verifiable identifier and QR-friendly code.
    """

    PENDING = 'pending'
    ISSUED = 'issued'
    REVOKED = 'revoked'
    STATUSES = [
        (PENDING, 'Pending'),
        (ISSUED, 'Issued'),
        (REVOKED, 'Revoked'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name='certificates')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE,
                                related_name='certificates')
    enrollment = models.OneToOneField('courses.Enrollment', on_delete=models.CASCADE,
                                       related_name='certificate', null=True, blank=True)

    # Unique verification identifier
    certificate_id = models.CharField(max_length=64, unique=True, editable=False)
    verification_code = models.UUIDField(default=uuid.uuid4, editable=False)

    # Issuing info
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='issued_certificates', blank=True,
    )
    issued_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUSES, default=PENDING)

    # PDF file
    pdf = models.FileField(upload_to='certificates/', null=True, blank=True)

    # Grading
    final_score_pct = models.PositiveIntegerField(default=0)
    grade = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('user', 'course')]
        ordering = ['-issued_at']

    def __str__(self):
        return f'Certificate: {self.user} - {self.course.title}'

    def save(self, *args, **kwargs):
        if not self.certificate_id:
            self.certificate_id = self._generate_id()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_id():
        # FTA = FinTech Accountant prefix + year + 8 random
        from django.utils.crypto import get_random_string
        year = timezone.now().year
        return f'FTA-{year}-{get_random_string(8, "ABCDEFGHJKLMNPQRSTUVWXYZ23456789")}'

    @property
    def is_platform_issued(self):
        """Always True - this app only issues platform course-completion
        certificates. Statutory qualifications live elsewhere."""
        return True

    @property
    def disclaimer(self):
        """Disclaimer printed on the certificate itself."""
        return (
            'This is a course-completion certificate issued by FinTech '
            'Accountant (fintechaccountant.com) and does not constitute a '
            'statutory professional qualification such as CA, CMA, CS, CPA '
            'or any qualification issued by an authorised awarding body.'
        )


class CertificateTemplate(models.Model):
    """A visual template for a certificate (branding / layout)."""

    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    template_html = models.TextField(help_text='Jinja/Django template HTML for the certificate PDF.')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_default', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_default:
            CertificateTemplate.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
