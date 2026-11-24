"""Networking app - news feed, posts, comments, likes, connections.

Implements the "Professional Network" pillar spec sections:
  - News Feed (posts, articles, images, discussions)
  - Connections (follow, connect, messaging lives in the messaging app)
"""
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# ---------------------------------------------------------------------------
# Connections (follow + connect)
# ---------------------------------------------------------------------------
class Connection(models.Model):
    """A directed follow or bidirectional connection between two users.

    A 'follow' is one-way (follower -> followee).
    A 'connect' is a two-way relationship requested then accepted.
    """

    FOLLOW = 'follow'
    CONNECT = 'connect'
    KINDS = [(FOLLOW, 'Follow'), (CONNECT, 'Connect')]

    PENDING = 'pending'
    ACCEPTED = 'accepted'
    DECLINED = 'declined'
    BLOCKED = 'blocked'
    STATUSES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (DECLINED, 'Declined'),
        (BLOCKED, 'Blocked'),
    ]

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='connections_sent',
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='connections_received',
    )
    kind = models.CharField(max_length=10, choices=KINDS, default=FOLLOW)
    status = models.CharField(max_length=10, choices=STATUSES, default=PENDING)
    message = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('from_user', 'to_user', 'kind')]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.from_user} -> {self.to_user} ({self.kind}, {self.status})'

    def accept(self):
        if self.kind == self.CONNECT and self.status == self.PENDING:
            self.status = self.ACCEPTED
            self.save(update_fields=['status', 'updated_at'])
            # Also create the reciprocal follow so both see each other's feed
            Connection.objects.get_or_create(
                from_user=self.to_user, to_user=self.from_user,
                kind=self.FOLLOW,
                defaults={'status': self.ACCEPTED},
            )
            self.from_user.profile.followers_count = self.from_user.profile.followers_count
            self.to_user.profile.followers_count = self.to_user.profile.followers_count
            self.from_user.profile.save(update_fields=['followers_count'])
            self.to_user.profile.save(update_fields=['followers_count'])


# ---------------------------------------------------------------------------
# Posts (the news feed)
# ---------------------------------------------------------------------------
class Post(models.Model):
    """A post on the news feed: status, article, image, link, or question."""

    STATUS = 'status'
    ARTICLE = 'article'
    QUESTION = 'question'
    IMAGE = 'image'
    LINK = 'link'
    TYPES = [
        (STATUS, 'Status'),
        (ARTICLE, 'Article'),
        (QUESTION, 'Question'),
        (IMAGE, 'Image'),
        (LINK, 'Link'),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='posts',
    )
    post_type = models.CharField(max_length=10, choices=TYPES, default=STATUS)
    title = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    image = models.ImageField(upload_to='posts/', null=True, blank=True)
    link_url = models.URLField(blank=True)

    # Tagging (communities etc.)
    communities = models.ManyToManyField('communities.Community',
                                          related_name='posts', blank=True)

    # Engagement (denormalised for fast display)
    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)

    is_pinned = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['post_type']),
        ]

    def __str__(self):
        return f'{self.author}: {self.title or self.body[:50]}'

    def increment_comments(self, delta=1):
        self.comments_count = max(0, self.comments_count + delta)
        self.save(update_fields=['comments_count'])

    def increment_likes(self, delta=1):
        self.likes_count = max(0, self.likes_count + delta)
        self.save(update_fields=['likes_count'])


# ---------------------------------------------------------------------------
# Engagement
# ---------------------------------------------------------------------------
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                               related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                related_name='replies')
    body = models.TextField()
    likes_count = models.PositiveIntegerField(default=0)
    is_flagged = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author}: {self.body[:50]}'

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)
        if is_new:
            self.post.increment_comments(1)


class Like(models.Model):
    """A like on a post or a comment (generic via target_post / target_comment)."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True,
                             related_name='likes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            ('user', 'post'),
            ('user', 'comment'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(post__isnull=False) | models.Q(comment__isnull=False),
                name='like_target_required',
            ),
        ]

    def __str__(self):
        target = self.post or self.comment
        return f'{self.user} likes {target}'
