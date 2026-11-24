"""URLs for the assessments app."""
from django.urls import path

from . import views

app_name = 'assessments'

urlpatterns = [
    path('', views.AssessmentListView.as_view(), name='list'),
    path('new/', views.AssessmentCreateView.as_view(), name='create'),
    path('<int:pk>/', views.AssessmentDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.AssessmentUpdateView.as_view(), name='edit'),
    path('<int:pk>/question/new/', views.QuestionCreateView.as_view(), name='question_create'),
    path('<int:pk>/take/', views.TakeAssessmentView.as_view(), name='take'),
    path('<int:pk>/result/', views.AssessmentResultView.as_view(), name='result'),
]
