"""Signals for the profiles app - auto-create a profile for each new user."""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from .models import Profile

User = get_user_model()


def _unique_slug(base):
    slug = slugify(base)[:100] or 'profile'
    candidate = slug
    i = 2
    while Profile.objects.filter(slug=candidate).exists():
        candidate = f'{slug}-{i}'
        i += 1
    return candidate


@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    """Every new user gets a Profile record on creation."""
    if created and not hasattr(instance, 'profile'):
        Profile.objects.create(
            user=instance,
            slug=_unique_slug(f'{instance.first_name}-{instance.last_name}-{instance.pk}'),
        )
