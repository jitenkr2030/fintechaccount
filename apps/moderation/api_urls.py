"""API URL routing for the moderation app."""
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .api_views import ReportViewSet, ModerationActionViewSet

router = DefaultRouter()
router.register('reports', ReportViewSet, basename='report')
router.register('actions', ModerationActionViewSet, basename='moderation-action')

urlpatterns = [
    path('', include(router.urls)),
]
