"""DRF serializers for the events app."""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Event, EventSpeaker, EventRegistration

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email']


class EventSpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSpeaker
        fields = ['id', 'event', 'name', 'title', 'bio', 'photo', 'linkedin']
        read_only_fields = ['event']


class EventRegistrationSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(read_only=True)

    class Meta:
        model = EventRegistration
        fields = ['id', 'event', 'user', 'attended', 'registered_at']
        read_only_fields = ['user', 'registered_at']


class EventSerializer(serializers.ModelSerializer):
    organiser = UserBriefSerializer(read_only=True)
    speakers = EventSpeakerSerializer(many=True, read_only=True)
    is_registered = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'title', 'slug', 'description', 'event_type', 'status',
                  'starts_at', 'ends_at', 'is_online', 'venue', 'city',
                  'meeting_url', 'cover_image', 'organiser', 'sponsor',
                  'max_attendees', 'is_paid', 'price', 'is_featured',
                  'registrations_count', 'is_registered', 'speakers',
                  'created_at', 'updated_at']
        read_only_fields = ['organiser', 'slug', 'registrations_count']

    def get_is_registered(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.registrations.filter(user=request.user).exists()

    def create(self, validated_data):
        validated_data['organiser'] = self.context['request'].user
        return super().create(validated_data)
