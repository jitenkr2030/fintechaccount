"""API URL routing for the payments app."""
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .api_views import OrderViewSet, SubscriptionViewSet

router = DefaultRouter()
router.register('orders', OrderViewSet, basename='order')
router.register('subscriptions', SubscriptionViewSet, basename='subscription')

urlpatterns = [
    path('', include(router.urls)),
]
