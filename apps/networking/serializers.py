"""DRF serializers for the networking app."""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Connection, Post, Comment, Like

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    avatar_url = serializers.ImageField(source='avatar', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'avatar_url', 'headline']


class CommentSerializer(serializers.ModelSerializer):
    author = UserBriefSerializer(read_only=True)
    user_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'parent', 'body',
                  'likes_count', 'user_liked', 'created_at']
        read_only_fields = ['post', 'author', 'likes_count', 'created_at']

    def get_user_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.likes.filter(user=request.user).exists()


class PostSerializer(serializers.ModelSerializer):
    author = UserBriefSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    user_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'post_type', 'title', 'body', 'image',
                  'link_url', 'likes_count', 'comments_count', 'shares_count',
                  'is_pinned', 'user_liked', 'comments', 'created_at']
        read_only_fields = ['author', 'likes_count', 'comments_count',
                            'shares_count', 'is_pinned']

    def get_user_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.likes.filter(user=request.user).exists()

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class ConnectionSerializer(serializers.ModelSerializer):
    from_user = UserBriefSerializer(read_only=True)
    to_user = UserBriefSerializer(read_only=True)

    class Meta:
        model = Connection
        fields = ['id', 'from_user', 'to_user', 'kind', 'status',
                  'message', 'created_at', 'updated_at']
        read_only_fields = ['from_user', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        request = self.context['request']
        target_id = request.data.get('to_user')
        if not target_id:
            raise serializers.ValidationError({'to_user': 'required.'})
        from django.contrib.auth import get_user_model
        target = get_user_model().objects.filter(pk=target_id).first()
        if not target:
            raise serializers.ValidationError({'to_user': 'not found.'})
        conn, created = Connection.objects.get_or_create(
            from_user=request.user, to_user=target,
            kind=validated_data.get('kind', Connection.FOLLOW),
            defaults={'status': Connection.ACCEPTED if validated_data.get('kind', Connection.FOLLOW) == Connection.FOLLOW else Connection.PENDING},
        )
        return conn
