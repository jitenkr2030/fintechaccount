"""Messaging app - direct messaging between users (Pillar A spec)."""
from django.conf import settings
from django.db import models


class Thread(models.Model):
    """A conversation between two or more users.

    For 1:1 conversations we look up the pair via the through model
    ThreadParticipant. Group chats are supported with ``is_group``.
    """

    subject = models.CharField(max_length=200, blank=True)
    is_group = models.BooleanField(default=False)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='ThreadParticipant',
        related_name='threads',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='created_threads',
    )
    last_message_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-last_message_at']

    def __str__(self):
        names = ', '.join(u.get_full_name() or u.email for u in self.participants.all()[:4])
        return f'Thread: {names}'

    @property
    def latest_message(self):
        return self.messages.order_by('-created_at').first()


class ThreadParticipant(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='thread_memberships')
    joined_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [('thread', 'user')]


class Message(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='sent_messages')
    body = models.TextField()
    attachment = models.FileField(upload_to='messages/', null=True, blank=True)
    read_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='read_messages',
                                      blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.sender}: {self.body[:50]}'
