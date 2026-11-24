"""DRF API views for the communities app."""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Community, CommunityMembership, CommunityTopic, CommunityReply
from .serializers import (
    CommunitySerializer, CommunityMembershipSerializer,
    CommunityTopicSerializer, CommunityReplySerializer,
)


class CommunityViewSet(viewsets.ModelViewSet):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filterset_fields = ['category', 'visibility', 'is_official']
    search_fields = ['name', 'description']

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(name__icontains=q) | qs.filter(description__icontains=q)
        return qs.distinct().order_by('-is_official', '-members_count')

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def join(self, request, slug=None):
        community = self.get_object()
        membership, created = CommunityMembership.objects.get_or_create(
            community=community, user=request.user,
            defaults={
                'status': CommunityMembership.PENDING
                if community.visibility != Community.PUBLIC
                else CommunityMembership.ACTIVE,
            },
        )
        if created and membership.status == CommunityMembership.ACTIVE:
            community.members_count += 1
            community.save(update_fields=['members_count'])
        return Response({
            'joined': created,
            'status': membership.status,
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def leave(self, request, slug=None):
        community = self.get_object()
        deleted, _ = CommunityMembership.objects.filter(
            community=community, user=request.user,
        ).delete()
        if deleted:
            community.members_count = max(0, community.members_count - 1)
            community.save(update_fields=['members_count'])
        return Response({'left': bool(deleted)})


class CommunityTopicViewSet(viewsets.ModelViewSet):
    queryset = CommunityTopic.objects.select_related('author', 'community')
    serializer_class = CommunityTopicSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['community']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommunityReplyViewSet(viewsets.ModelViewSet):
    queryset = CommunityReply.objects.select_related('author', 'topic')
    serializer_class = CommunityReplySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['topic']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
