"""API URL routing for the events app."""
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .api_views import (
    EventViewSet, EventSpeakerViewSet, EventRegistrationViewSet,
)

router = DefaultRouter()
router.register('events', EventViewSet, basename='event')
router.register('speakers', EventSpeakerViewSet, basename='speaker')
router.register('registrations', EventRegistrationViewSet, basename='registration')

urlpatterns = [
    path('', include(router.urls)),
]
