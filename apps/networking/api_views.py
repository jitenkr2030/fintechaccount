"""DRF API views for the networking app."""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

from .models import Connection, Post, Comment, Like
from .serializers import (
    PostSerializer, CommentSerializer, ConnectionSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Post.objects.select_related('author', 'author__profile').prefetch_related(
            'comments', 'likes',
        )
        feed = self.request.query_params.get('feed')
        if feed == 'me' and self.request.user.is_authenticated:
            following_ids = list(Connection.objects.filter(
                from_user=self.request.user, status=Connection.ACCEPTED,
            ).values_list('to_user_id', flat=True))
            following_ids.append(self.request.user.id)
            qs = qs.filter(Q(author_id__in=following_ids) | Q(is_pinned=True))
        elif feed == 'trending':
            qs = qs.order_by('-likes_count', '-comments_count')
        return qs.distinct().order_by('-is_pinned', '-created_at')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        like = Like.objects.filter(user=request.user, post=post).first()
        if like:
            like.delete()
            post.increment_likes(-1)
            return Response({'liked': False, 'count': post.likes_count})
        Like.objects.create(user=request.user, post=post)
        post.increment_likes(1)
        return Response({'liked': True, 'count': post.likes_count})


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Comment.objects.select_related('author', 'post')
        post_id = self.request.query_params.get('post')
        if post_id:
            qs = qs.filter(post_id=post_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class ConnectionViewSet(viewsets.ModelViewSet):
    serializer_class = ConnectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        which = self.request.query_params.get('which', 'all')
        qs = Connection.objects.select_related('from_user', 'to_user')
        if which == 'following':
            return qs.filter(from_user=user, kind=Connection.FOLLOW)
        if which == 'followers':
            return qs.filter(to_user=user, kind=Connection.FOLLOW)
        if which == 'pending':
            return qs.filter(to_user=user, status=Connection.PENDING)
        return qs.filter(Q(from_user=user) | Q(to_user=user))

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def accept(self, request, pk=None):
        conn = self.get_object()
        if conn.to_user_id != request.user.id:
            return Response({'detail': 'Not allowed.'},
                            status=status.HTTP_403_FORBIDDEN)
        conn.accept()
        return Response(ConnectionSerializer(conn, context={'request': request}).data)
