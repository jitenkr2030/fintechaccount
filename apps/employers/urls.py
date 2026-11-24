"""URLs for the employers app."""
from django.urls import path

from . import views

app_name = 'employers'

urlpatterns = [
    path('', views.EmployerListView.as_view(), name='list'),
    path('become/', views.BecomeEmployerView.as_view(), name='become'),
    path('dashboard/', views.EmployerDashboardView.as_view(), name='dashboard'),
    path('edit/', views.EmployerProfileEditView.as_view(), name='edit'),
    path('candidates/', views.CandidateSearchView.as_view(), name='candidate_search'),
    path('<slug:slug>/', views.EmployerDetailView.as_view(), name='detail'),
]
