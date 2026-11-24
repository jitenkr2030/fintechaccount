"""API URL routing for the courses app."""
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .api_views import (
    CategoryViewSet, CourseViewSet, ModuleViewSet, LessonViewSet,
    EnrollmentViewSet, LessonProgressViewSet, CourseReviewViewSet,
)

router = DefaultRouter()
router.register('categories', CategoryViewSet, basename='category')
router.register('courses', CourseViewSet, basename='course')
router.register('modules', ModuleViewSet, basename='module')
router.register('lessons', LessonViewSet, basename='lesson')
router.register('enrollments', EnrollmentViewSet, basename='enrollment')
router.register('progress', LessonProgressViewSet, basename='progress')
router.register('reviews', CourseReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
]
