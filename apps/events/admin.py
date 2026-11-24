"""Admin for the events app."""
from django.contrib import admin

from .models import Event, EventSpeaker, EventRegistration


class SpeakerInline(admin.TabularInline):
    model = EventSpeaker
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'status', 'starts_at',
                    'is_online', 'is_paid', 'is_featured', 'registrations_count')
    list_filter = ('event_type', 'status', 'is_online', 'is_paid', 'is_featured')
    search_fields = ('title', 'description', 'venue', 'city')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [SpeakerInline]
    readonly_fields = ('registrations_count',)


admin.site.register(EventSpeaker)
admin.site.register(EventRegistration)
