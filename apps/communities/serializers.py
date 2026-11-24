"""DRF serializers for the communities app."""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Community, CommunityMembership, CommunityTopic, CommunityReply

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'headline']


class CommunityReplySerializer(serializers.ModelSerializer):
    author = UserBriefSerializer(read_only=True)

    class Meta:
        model = CommunityReply
        fields = ['id', 'topic', 'author', 'body', 'created_at']
        read_only_fields = ['topic', 'author', 'created_at']


class CommunityTopicSerializer(serializers.ModelSerializer):
    author = UserBriefSerializer(read_only=True)
    replies = CommunityReplySerializer(many=True, read_only=True)

    class Meta:
        model = CommunityTopic
        fields = ['id', 'community', 'author', 'title', 'body',
                  'is_pinned', 'views_count', 'replies_count',
                  'replies', 'created_at']
        read_only_fields = ['author', 'is_pinned', 'views_count', 'replies_count']


class CommunityMembershipSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(read_only=True)

    class Meta:
        model = CommunityMembership
        fields = ['id', 'community', 'user', 'role', 'status', 'joined_at']
        read_only_fields = ['user', 'joined_at']


class CommunitySerializer(serializers.ModelSerializer):
    owner = UserBriefSerializer(read_only=True)
    is_member = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = ['id', 'name', 'slug', 'description', 'category', 'visibility',
                  'owner', 'is_official', 'members_count', 'posts_count',
                  'is_member', 'created_at']
        read_only_fields = ['owner', 'slug', 'is_official',
                            'members_count', 'posts_count']

    def get_is_member(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.members.filter(id=request.user.id).exists()

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)
