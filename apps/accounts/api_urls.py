"""API URL routing for the accounts app."""
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .api_views import RoleViewSet, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='user')
router.register('roles', RoleViewSet, basename='role')

urlpatterns = [
    path('', include(router.urls)),
]
