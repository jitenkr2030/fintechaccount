"""Signals for the accounts app."""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, Role


@receiver(post_save, sender=User)
def ensure_default_role(sender, instance, created, **kwargs):
    """Assign the default 'student' role to brand-new non-superuser accounts so
    they have at least one role while completing their profile.
    """
    if not created:
        return
    if instance.is_superuser:
        return
    if instance.roles.exists():
        return
    student = Role.objects.filter(name=Role.STUDENT).first()
    if student:
        instance.roles.add(student)
