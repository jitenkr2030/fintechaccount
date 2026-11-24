"""API URL routing for the profiles app."""
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .api_views import (
    SkillViewSet, ProfileViewSet, EducationViewSet, ExperienceViewSet,
    CertificationViewSet, ProfileSkillViewSet, PortfolioItemViewSet,
)

router = DefaultRouter()
router.register('skills', SkillViewSet, basename='skill')
router.register('profiles', ProfileViewSet, basename='profile')
router.register('educations', EducationViewSet, basename='education')
router.register('experiences', ExperienceViewSet, basename='experience')
router.register('certifications', CertificationViewSet, basename='certification')
router.register('profile-skills', ProfileSkillViewSet, basename='profile-skill')
router.register('portfolio-items', PortfolioItemViewSet, basename='portfolio-item')

urlpatterns = [
    path('', include(router.urls)),
]
