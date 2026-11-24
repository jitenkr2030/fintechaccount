"""DRF API views for the notifications app."""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Notification, Announcement
from .serializers import NotificationSerializer, AnnouncementSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['category', 'is_read']

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_read(self, request, pk=None):
        n = self.get_object()
        n.is_read = True
        n.save(update_fields=['is_read'])
        return Response(NotificationSerializer(n).data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_all_read(self, request):
        Notification.objects.filter(
            recipient=request.user, is_read=False,
        ).update(is_read=True)
        return Response({'marked': True})

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def unread_count(self, request):
        count = Notification.objects.filter(
            recipient=request.user, is_read=False,
        ).count()
        return Response({'unread': count})


class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['is_pinned', 'is_published']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_admin_role:
            return qs
        return qs.filter(is_published=True)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
