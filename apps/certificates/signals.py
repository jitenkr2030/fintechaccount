"""Signals for the certificates app - auto-issue on course completion."""
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.courses.models import Enrollment
from .models import Certificate


@receiver(post_save, sender=Enrollment)
def issue_certificate_on_completion(sender, instance, created, **kwargs):
    """Auto-issue a certificate when an enrollment reaches COMPLETED.

    Only when the course is marked ``is_certified`` (i.e. the platform issues
    a completion certificate for it).
    """
    if instance.status != Enrollment.COMPLETED:
        return
    if not instance.course.is_certified:
        return
    Certificate.objects.get_or_create(
        user=instance.student, course=instance.course,
        defaults={
            'enrollment': instance,
            'status': Certificate.ISSUED,
            'final_score_pct': instance.progress_pct,
        },
    )
