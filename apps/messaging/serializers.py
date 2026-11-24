"""DRF serializers for the messaging app."""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Thread, Message, ThreadParticipant

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email']


class MessageSerializer(serializers.ModelSerializer):
    sender = UserBriefSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'thread', 'sender', 'body', 'attachment',
                  'created_at', 'read_by']
        read_only_fields = ['sender', 'read_by']


class ThreadSerializer(serializers.ModelSerializer):
    participants = UserBriefSerializer(many=True, read_only=True)
    latest_message = MessageSerializer(read_only=True)
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = ['id', 'subject', 'is_group', 'participants',
                  'latest_message', 'unread_count', 'last_message_at', 'created_at']
        read_only_fields = ['participants', 'latest_message', 'last_message_at']

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0
        membership = ThreadParticipant.objects.filter(
            thread=obj, user=request.user,
        ).first()
        last_read = membership.last_read_at if membership else None
        qs = obj.messages.exclude(sender=request.user)
        if last_read:
            qs = qs.filter(created_at__gt=last_read)
        return qs.count()
