"""Communities app - groups and communities (Pillar A spec).

Pre-seeded example communities per the spec:
  - Chartered Accountants Network
  - GST Practitioners Community
  - Tally & Accounting Professionals
  - Banking & Financial Services
  - FinTech Developers
  - Investment & Capital Markets
  - Excel and Financial Modelling
  - Finance Students Community

Professional groups per spec: CA, CMA, CS, accountants, students.
"""
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Community(models.Model):
    """A professional community or group.

    ``is_official`` flags communities run by the platform. All others are
    user-created subject to moderation.
    """

    PUBLIC = 'public'
    PRIVATE = 'private'
    RESTRICTED = 'restricted'
    VISIBILITY = [
        (PUBLIC, 'Public'),
        (PRIVATE, 'Private (request to join)'),
        (RESTRICTED, 'Restricted (invite only)'),
    ]

    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField()
    icon = models.ImageField(upload_to='communities/', null=True, blank=True)
    category = models.CharField(max_length=80, blank=True,
                                help_text='e.g. Accounting, Tax, FinTech, Banking, Students')
    visibility = models.CharField(max_length=20, choices=VISIBILITY, default=PUBLIC)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='owned_communities',
    )
    moderators = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='moderated_communities', blank=True,
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='communities', blank=True,
        through='CommunityMembership',
    )

    is_official = models.BooleanField(default=False)
    members_count = models.PositiveIntegerField(default=0)
    posts_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'communities'
        ordering = ['-is_official', '-members_count', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)


class CommunityMembership(models.Model):
    """Through-model: a user's membership of a community."""

    MEMBER = 'member'
    MODERATOR = 'moderator'
    OWNER = 'owner'
    ROLES = [
        (MEMBER, 'Member'),
        (MODERATOR, 'Moderator'),
        (OWNER, 'Owner'),
    ]

    PENDING = 'pending'
    ACTIVE = 'active'
    BANNED = 'banned'
    STATUSES = [
        (PENDING, 'Pending'),
        (ACTIVE, 'Active'),
        (BANNED, 'Banned'),
    ]

    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='community_memberships')
    role = models.CharField(max_length=20, choices=ROLES, default=MEMBER)
    status = models.CharField(max_length=20, choices=STATUSES, default=ACTIVE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('community', 'user')]
        ordering = ['-joined_at']

    def __str__(self):
        return f'{self.user} in {self.community} ({self.role})'


class CommunityTopic(models.Model):
    """A discussion topic / thread inside a community."""

    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='topics')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='community_topics')
    title = models.CharField(max_length=200)
    body = models.TextField()
    is_pinned = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    replies_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title


class CommunityReply(models.Model):
    topic = models.ForeignKey(CommunityTopic, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='community_replies')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Reply by {self.author} on {self.topic}'
