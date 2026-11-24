"""Admin for the notifications app."""
from django.contrib import admin

from .models import Notification, Announcement


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'actor', 'category', 'verb',
                    'target_text', 'is_read', 'created_at')
    list_filter = ('category', 'is_read')
    search_fields = ('recipient__email', 'actor__email', 'verb', 'target_text')
    readonly_fields = ('created_at',)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_pinned', 'is_published',
                    'created_by', 'created_at')
    list_filter = ('is_pinned', 'is_published')
    search_fields = ('title', 'body')
    readonly_fields = ('created_at', 'updated_at')
