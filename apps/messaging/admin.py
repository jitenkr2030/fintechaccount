"""Admin for the messaging app."""
from django.contrib import admin

from .models import Thread, ThreadParticipant, Message


class ThreadParticipantInline(admin.TabularInline):
    model = ThreadParticipant
    extra = 1


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('sender', 'body', 'created_at')


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'is_group', 'last_message_at', 'created_at')
    list_filter = ('is_group',)
    search_fields = ('subject',)
    inlines = [ThreadParticipantInline, MessageInline]


admin.site.register(Message)
admin.site.register(ThreadParticipant)
