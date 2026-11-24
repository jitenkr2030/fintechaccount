"""API URL routing for the employers app."""
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .api_views import EmployerProfileViewSet, InterviewViewSet

router = DefaultRouter()
router.register('employers', EmployerProfileViewSet, basename='employer')
router.register('interviews', InterviewViewSet, basename='interview')

urlpatterns = [
    path('', include(router.urls)),
]
