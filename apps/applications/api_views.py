"""DRF API views for the applications app."""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import JobApplication
from .serializers import JobApplicationSerializer


class JobApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'job']

    def get_queryset(self):
        qs = JobApplication.objects.select_related('applicant', 'job', 'job__employer')
        if self.request.user.is_admin_role:
            return qs
        # Applicant sees their own; employer sees their job's applications
        return qs.filter(applicant=self.request.user) | \
            qs.filter(job__posted_by=self.request.user)

    def perform_create(self, serializer):
        # Only allow the applicant themselves to create
        serializer.save(applicant=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def update_status(self, request, pk=None):
        app = self.get_object()
        if app.job.posted_by_id != request.user.id and not request.user.is_admin_role:
            return Response({'detail': 'Only the employer can update status.'},
                            status=status.HTTP_403_FORBIDDEN)
        new_status = request.data.get('status')
        valid = {s for s, _ in JobApplication.STATUSES}
        if new_status not in valid:
            return Response({'detail': 'Invalid status.'},
                            status=status.HTTP_400_BAD_REQUEST)
        app.status = new_status
        app.save(update_fields=['status', 'updated_at'])
        return Response(JobApplicationSerializer(app).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def withdraw(self, request, pk=None):
        app = self.get_object()
        if app.applicant_id != request.user.id:
            return Response({'detail': 'Only the applicant can withdraw.'},
                            status=status.HTTP_403_FORBIDDEN)
        app.status = JobApplication.WITHDRAWN
        app.save(update_fields=['status', 'updated_at'])
        return Response({'withdrawn': True})
