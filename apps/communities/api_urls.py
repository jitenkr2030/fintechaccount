"""API URL routing for the communities app."""
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .api_views import (
    CommunityViewSet, CommunityTopicViewSet, CommunityReplyViewSet,
)

router = DefaultRouter()
router.register('communities', CommunityViewSet, basename='community')
router.register('topics', CommunityTopicViewSet, basename='topic')
router.register('replies', CommunityReplyViewSet, basename='reply')

urlpatterns = [
    path('', include(router.urls)),
]
