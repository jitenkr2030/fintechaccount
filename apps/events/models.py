"""Events app - webinars, seminars, workshops (Pillar A spec).

Implements the Events module of the Professional Network pillar.
Sponsored webinars/events can be paid (revenue model: Sponsorship).
"""
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Event(models.Model):
    WEBINAR = 'webinar'
    SEMINAR = 'seminar'
    WORKSHOP = 'workshop'
    CONFERENCE = 'conference'
    MEETUP = 'meetup'
    TYPES = [
        (WEBINAR, 'Webinar'),
        (SEMINAR, 'Seminar'),
        (WORKSHOP, 'Workshop'),
        (CONFERENCE, 'Conference'),
        (MEETUP, 'Meetup'),
    ]

    DRAFT = 'draft'
    PUBLISHED = 'published'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'
    STATUSES = [
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
        (CANCELLED, 'Cancelled'),
        (COMPLETED, 'Completed'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=TYPES, default=WEBINAR)
    status = models.CharField(max_length=20, choices=STATUSES, default=PUBLISHED)

    # Schedule
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField(null=True, blank=True)

    # Online / offline
    is_online = models.BooleanField(default=True)
    venue = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=80, blank=True)
    meeting_url = models.URLField(blank=True, help_text='Zoom / Google Meet / YouTube Live URL')

    # Cover image
    cover_image = models.ImageField(upload_to='events/', null=True, blank=True)

    # Organiser / sponsors
    organiser = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='organised_events',
    )
    sponsor = models.CharField(max_length=200, blank=True)

    # Capacity & pricing
    max_attendees = models.PositiveIntegerField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_featured = models.BooleanField(default=False)

    registrations_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-starts_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:220] or f'event-{self.id or "draft"}'
            candidate = base
            i = 2
            while Event.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f'{base}-{i}'
                i += 1
            self.slug = candidate
        super().save(*args, **kwargs)


class EventSpeaker(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='speakers')
    name = models.CharField(max_length=120)
    title = models.CharField(max_length=200, blank=True,
                             help_text='e.g. CFO at XYZ, CA, GST Expert')
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='event_speakers/', null=True, blank=True)
    linkedin = models.URLField(blank=True)

    def __str__(self):
        return f'{self.name} ({self.event.title})'


class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='event_registrations')
    attended = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('event', 'user')]

    def __str__(self):
        return f'{self.user} -> {self.event}'
