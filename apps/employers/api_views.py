"""DRF API views for the employers app."""
from rest_framework import viewsets, permissions

from .models import EmployerProfile, Interview
from .serializers import EmployerProfileSerializer, InterviewSerializer


class EmployerProfileViewSet(viewsets.ModelViewSet):
    queryset = EmployerProfile.objects.select_related('user').all()
    serializer_class = EmployerProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    search_fields = ['company_name', 'about', 'industry', 'headquarters_city']

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(
                company_name__icontains=q,
            ) | qs.filter(about__icontains=q) \
              | qs.filter(industry__icontains=q) \
              | qs.filter(headquarters_city__icontains=q)
        return qs.distinct().order_by('-is_verified', 'company_name')


class InterviewViewSet(viewsets.ModelViewSet):
    queryset = Interview.objects.select_related('application', 'interviewer').all()
    serializer_class = InterviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['application', 'status', 'interviewer']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_admin_role:
            return qs
        # Employer sees interviews for their jobs; applicant sees their own
        return qs.filter(
            application__applicant=self.request.user
        ) | qs.filter(application__job__posted_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(interviewer=self.request.user)
