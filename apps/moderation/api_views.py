"""DRF API views for the moderation app."""
from rest_framework import viewsets, permissions

from .models import Report, ModerationAction
from .serializers import ReportSerializer, ModerationActionSerializer


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.select_related('reporter', 'assigned_to').all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'reason', 'target_type']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_admin_role:
            return qs
        return qs.filter(reporter=self.request.user)

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)


class ModerationActionViewSet(viewsets.ModelViewSet):
    queryset = ModerationAction.objects.select_related('admin', 'report').all()
    serializer_class = ModerationActionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['report', 'action']

    def perform_create(self, serializer):
        serializer.save(admin=self.request.user)
