"""API URL routing for the messaging app."""
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .api_views import ThreadViewSet, MessageViewSet

router = DefaultRouter()
router.register('threads', ThreadViewSet, basename='thread')
router.register('messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
]
