"""API URL routing for the careers app."""
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .api_views import JobViewSet, JobCategoryViewSet, JobAlertViewSet

router = DefaultRouter()
router.register('jobs', JobViewSet, basename='job')
router.register('categories', JobCategoryViewSet, basename='job-category')
router.register('alerts', JobAlertViewSet, basename='job-alert')

urlpatterns = [
    path('', include(router.urls)),
]
