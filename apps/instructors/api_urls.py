"""API URL routing for the instructors app."""
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .api_views import InstructorProfileViewSet, PayoutViewSet

router = DefaultRouter()
router.register('instructors', InstructorProfileViewSet, basename='instructor')
router.register('payouts', PayoutViewSet, basename='payout')

urlpatterns = [
    path('', include(router.urls)),
]
