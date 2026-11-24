"""DRF API views for the profiles app."""
from rest_framework import viewsets, permissions

from .models import (
    Skill, Profile, Education, Experience, Certification,
    ProfileSkill, PortfolioItem,
)
from .serializers import (
    SkillSerializer, ProfileSerializer, EducationSerializer,
    ExperienceSerializer, CertificationSerializer, ProfileSkillSerializer,
    PortfolioItemSerializer,
)


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    search_fields = ['name', 'category']
    filterset_fields = ['category']


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.select_related('user').all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get('q')
        industry = self.request.query_params.get('industry')
        if q:
            qs = qs.filter(
                user__first_name__icontains=q
            ) | qs.filter(user__last_name__icontains=q) \
              | qs.filter(current_title__icontains=q) \
              | qs.filter(current_company__icontains=q)
        if industry:
            qs = qs.filter(industry__icontains=industry)
        return qs.distinct()


class EducationViewSet(viewsets.ModelViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    permission_classes = [permissions.IsAuthenticated]


class ExperienceViewSet(viewsets.ModelViewSet):
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]


class CertificationViewSet(viewsets.ModelViewSet):
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['is_statutory', 'is_verified']


class ProfileSkillViewSet(viewsets.ModelViewSet):
    queryset = ProfileSkill.objects.all()
    serializer_class = ProfileSkillSerializer
    permission_classes = [permissions.IsAuthenticated]


class PortfolioItemViewSet(viewsets.ModelViewSet):
    queryset = PortfolioItem.objects.all()
    serializer_class = PortfolioItemSerializer
    permission_classes = [permissions.IsAuthenticated]
