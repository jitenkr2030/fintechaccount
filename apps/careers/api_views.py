"""DRF API views for the careers app."""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone

from .models import Job, JobCategory, JobAlert
from .serializers import (
    JobSerializer, JobBriefSerializer, JobCategorySerializer, JobAlertSerializer,
)


class JobCategoryViewSet(viewsets.ModelViewSet):
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'


class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    filterset_fields = ['category', 'employment_type', 'experience_level',
                        'is_remote', 'is_wfh', 'is_featured', 'status']
    search_fields = ['title', 'description', 'skills_required',
                     'location_city', 'employer__company_name']

    def get_queryset(self):
        # Non-staff only see open jobs
        if self.action == 'list':
            qs = Job.objects.filter(status=Job.OPEN)
        else:
            qs = Job.objects.all()
        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(
                Q(title__icontains=q) | Q(description__icontains=q)
                | Q(skills_required__icontains=q)
                | Q(employer__company_name__icontains=q)
            )
        return qs.exclude(
            application_deadline__lt=timezone.now(),
        ).order_by('-is_featured', '-posted_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return JobBriefSerializer
        return JobSerializer

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def featured(self, request):
        qs = Job.objects.filter(is_featured=True, status=Job.OPEN)[:10]
        return Response(JobBriefSerializer(qs, many=True).data)


class JobAlertViewSet(viewsets.ModelViewSet):
    serializer_class = JobAlertSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JobAlert.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
