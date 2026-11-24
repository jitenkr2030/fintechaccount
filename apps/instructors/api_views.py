"""DRF API views for the instructors app."""
from rest_framework import viewsets, permissions

from .models import InstructorProfile, Payout
from .serializers import InstructorProfileSerializer, PayoutSerializer


class InstructorProfileViewSet(viewsets.ModelViewSet):
    queryset = InstructorProfile.objects.select_related('user').all()
    serializer_class = InstructorProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    search_fields = ['title', 'expertise', 'bio']


class PayoutViewSet(viewsets.ModelViewSet):
    queryset = Payout.objects.select_related('instructor').all()
    serializer_class = PayoutSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['instructor', 'status']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_admin_role:
            return qs
        # Instructors see only their own payouts
        if hasattr(self.request.user, 'instructor_profile'):
            return qs.filter(instructor=self.request.user.instructor_profile)
        return qs.none()
