"""DRF API views for the events app."""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone

from .models import Event, EventSpeaker, EventRegistration
from .serializers import (
    EventSerializer, EventSpeakerSerializer, EventRegistrationSerializer,
)


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filterset_fields = ['event_type', 'status', 'is_online', 'is_paid']
    search_fields = ['title', 'description', 'venue', 'city']

    def get_queryset(self):
        qs = Event.objects.filter(status=Event.PUBLISHED)
        q = self.request.query_params.get('q')
        upcoming = self.request.query_params.get('upcoming')
        if q:
            qs = qs.filter(
                Q(title__icontains=q) | Q(description__icontains=q)
                | Q(city__icontains=q) | Q(venue__icontains=q)
            )
        if upcoming == '1':
            qs = qs.filter(starts_at__gt=timezone.now())
        return qs.order_by('-is_featured', '-starts_at')

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def register(self, request, slug=None):
        event = self.get_object()
        reg, created = EventRegistration.objects.get_or_create(
            event=event, user=request.user,
        )
        if created:
            event.registrations_count += 1
            event.save(update_fields=['registrations_count'])
        return Response(EventRegistrationSerializer(reg).data,
                        status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class EventSpeakerViewSet(viewsets.ModelViewSet):
    queryset = EventSpeaker.objects.all()
    serializer_class = EventSpeakerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ['event']


class EventRegistrationViewSet(viewsets.ModelViewSet):
    queryset = EventRegistration.objects.all()
    serializer_class = EventRegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['event', 'user']

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_admin_role:
            qs = qs.filter(user=self.request.user)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
