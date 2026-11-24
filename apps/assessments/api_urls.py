"""API URL routing for the assessments app."""
from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .api_views import (
    AssessmentViewSet, QuestionViewSet, ChoiceViewSet,
    AssessmentAttemptViewSet, AnswerViewSet,
)

router = DefaultRouter()
router.register('assessments', AssessmentViewSet, basename='assessment')
router.register('questions', QuestionViewSet, basename='question')
router.register('choices', ChoiceViewSet, basename='choice')
router.register('attempts', AssessmentAttemptViewSet, basename='attempt')
router.register('answers', AnswerViewSet, basename='answer')

urlpatterns = [
    path('', include(router.urls)),
]
