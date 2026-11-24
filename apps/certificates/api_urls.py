"""API URL routing for the certificates app."""
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .api_views import CertificateViewSet, CertificateTemplateViewSet

router = DefaultRouter()
router.register('certificates', CertificateViewSet, basename='certificate')
router.register('templates', CertificateTemplateViewSet, basename='template')

urlpatterns = [
    path('', include(router.urls)),
]
