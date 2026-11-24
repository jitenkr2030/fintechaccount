"""Analytics app - dashboards & AI recommendation stubs (Phase 5 spec).

Phase 5 spec items:
  - AI career recommendations (stub: content-based filtering on profile skills)
  - AI learning assistant (stub: keyword-based course suggestions)
  - Skill assessment analytics
  - Recruitment analytics
  - Institutional partnerships reporting

AI features are heuristic stubs that compute recommendations from existing
profile/skill/enrollment data. The surface area (views, API, dashboard) is in
place so it can be upgraded to a real model later.
"""
from django.conf import settings
from django.db import models


class UserActivity(models.Model):
    """Aggregated daily activity per user (denormalised for dashboards)."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name='daily_activities')
    date = models.DateField()
    posts_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    logins_count = models.PositiveIntegerField(default=0)
    course_minutes = models.PositiveIntegerField(default=0,
                                                  help_text='Minutes spent on courses')

    class Meta:
        unique_together = [('user', 'date')]
        ordering = ['-date']


class Recommendation(models.Model):
    """A generated recommendation (course or job) for a user."""

    CAREER = 'career'
    LEARNING = 'learning'
    SOURCES = [(CAREER, 'Career'), (LEARNING, 'Learning')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                              related_name='recommendations')
    source = models.CharField(max_length=20, choices=SOURCES)
    target_type = models.CharField(max_length=40,
                                    help_text='course, job, skill, etc.')
    target_id = models.PositiveIntegerField(null=True, blank=True)
    target_text = models.CharField(max_length=300)
    target_url = models.URLField(blank=True)
    reason = models.CharField(max_length=300, blank=True)
    score = models.FloatField(default=0, help_text='Match score 0-1')
    is_dismissed = models.BooleanField(default=False)
    is_clicked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score', '-created_at']
        indexes = [models.Index(fields=['user', 'source', '-score'])]

    def __str__(self):
        return f'{self.user} <- {self.source}:{self.target_text}'
