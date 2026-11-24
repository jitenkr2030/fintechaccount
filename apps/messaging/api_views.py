"""DRF API views for the messaging app."""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Thread, Message, ThreadParticipant
from .serializers import ThreadSerializer, MessageSerializer

User = get_user_model()


class ThreadViewSet(viewsets.ModelViewSet):
    serializer_class = ThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Thread.objects.filter(participants=self.request.user).order_by('-last_message_at')

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def send(self, request, pk=None):
        thread = self.get_object()
        if not thread.participants.filter(id=request.user.id).exists():
            return Response({'detail': 'Not a participant.'},
                            status=status.HTTP_403_FORBIDDEN)
        body = request.data.get('body', '').strip()
        if not body:
            return Response({'detail': 'body is required.'},
                            status=status.HTTP_400_BAD_REQUEST)
        msg = Message.objects.create(thread=thread, sender=request.user, body=body)
        thread.last_message_at = msg.created_at
        thread.save(update_fields=['last_message_at'])
        return Response(MessageSerializer(msg).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def mark_read(self, request, pk=None):
        thread = self.get_object()
        membership = ThreadParticipant.objects.filter(
            thread=thread, user=request.user,
        ).first()
        if membership:
            membership.last_read_at = timezone.now()
            membership.save(update_fields=['last_read_at'])
        return Response({'marked': True})


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Message.objects.filter(thread__participants=self.request.user)
        thread_id = self.request.query_params.get('thread')
        if thread_id:
            qs = qs.filter(thread_id=thread_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
