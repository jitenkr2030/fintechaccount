"""API URL routing for the networking app."""
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .api_views import PostViewSet, CommentViewSet, ConnectionViewSet

router = DefaultRouter()
router.register('posts', PostViewSet, basename='post')
router.register('comments', CommentViewSet, basename='comment')
router.register('connections', ConnectionViewSet, basename='connection')

urlpatterns = [
    path('', include(router.urls)),
]
