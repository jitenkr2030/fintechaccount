"""Admin for the moderation app."""
from django.contrib import admin

from .models import Report, ModerationAction


class ModerationActionInline(admin.TabularInline):
    model = ModerationAction
    extra = 0
    readonly_fields = ('admin', 'action', 'notes', 'created_at')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('target_type', 'target_id', 'reason', 'status',
                    'reporter', 'assigned_to', 'created_at')
    list_filter = ('status', 'reason', 'target_type')
    search_fields = ('description', 'resolution_notes', 'target_url')
    readonly_fields = ('reporter', 'target_type', 'target_id', 'target_url',
                       'reason', 'description', 'created_at', 'updated_at')
    inlines = [ModerationActionInline]


admin.site.register(ModerationAction)
