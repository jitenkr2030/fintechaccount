"""DRF serializers for the notifications app."""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Notification, Announcement

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email']


class NotificationSerializer(serializers.ModelSerializer):
    actor = UserBriefSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'actor', 'category', 'verb',
                  'target_text', 'target_url', 'is_read', 'is_emailed',
                  'created_at']
        read_only_fields = ['recipient', 'actor', 'category', 'verb',
                            'target_text', 'target_url', 'is_emailed',
                            'created_at']


class AnnouncementSerializer(serializers.ModelSerializer):
    created_by = UserBriefSerializer(read_only=True)

    class Meta:
        model = Announcement
        fields = ['id', 'title', 'body', 'is_pinned', 'is_published',
                  'created_by', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at']
