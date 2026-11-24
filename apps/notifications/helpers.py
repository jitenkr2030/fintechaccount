"""Helper to send notifications across the platform.

Usage:
    from apps.notifications.helpers import notify
    notify(recipient=user, actor=other_user, verb='liked your post',
           category=Notification.NETWORK, target_text='Post #42',
           target_url='/network/post/42/')
"""
from django.contrib.auth import get_user_model

from .models import Notification


def notify(recipient, actor=None, verb='', category=Notification.SYSTEM,
           target_text='', target_url=''):
    """Create a notification for ``recipient``."""
    if recipient is None:
        return None
    if isinstance(recipient, str):
        User = get_user_model()
        recipient = User.objects.filter(email=recipient).first()
        if not recipient:
            return None
    return Notification.objects.create(
        recipient=recipient,
        actor=actor,
        category=category,
        verb=verb,
        target_text=target_text,
        target_url=target_url,
    )


def notify_many(recipients, **kwargs):
    """Send the same notification to multiple recipients."""
    notifications = []
    for r in recipients:
        n = notify(recipient=r, **kwargs)
        if n:
            notifications.append(n)
    return notifications
