"""URLs for the careers app."""
from django.urls import path

from . import views

app_name = 'careers'

urlpatterns = [
    path('', views.JobListView.as_view(), name='list'),
    path('new/', views.JobCreateView.as_view(), name='create'),
    path('my-jobs/', views.EmployerJobsView.as_view(), name='employer_jobs'),
    path('my-alerts/', views.MyAlertsView.as_view(), name='my_alerts'),
    path('alert/new/', views.JobAlertCreateView.as_view(), name='alert_create'),
    path('alert/<int:pk>/toggle/', views.AlertToggleView.as_view(), name='alert_toggle'),
    path('<slug:slug>/', views.JobDetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', views.JobUpdateView.as_view(), name='edit'),
    path('<slug:slug>/delete/', views.JobDeleteView.as_view(), name='delete'),
]
