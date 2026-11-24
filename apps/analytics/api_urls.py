from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .api_views import RecommendationViewSet, UserActivityViewSet

router = DefaultRouter()
router.register('recommendations', RecommendationViewSet, basename='recommendation')
router.register('activity', UserActivityViewSet, basename='activity')

urlpatterns = [path('', include(router.urls))]
