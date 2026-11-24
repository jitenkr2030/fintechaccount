"""API URL routing for the applications app."""
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .api_views import JobApplicationViewSet

router = DefaultRouter()
router.register('applications', JobApplicationViewSet, basename='application')

urlpatterns = [
    path('', include(router.urls)),
]
