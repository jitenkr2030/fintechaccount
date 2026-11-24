"""API URL routing for the notifications app."""
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .api_views import NotificationViewSet, AnnouncementViewSet

router = DefaultRouter()
router.register('notifications', NotificationViewSet, basename='notification')
router.register('announcements', AnnouncementViewSet, basename='announcement')

urlpatterns = [
    path('', include(router.urls)),
]
