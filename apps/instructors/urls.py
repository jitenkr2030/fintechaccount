"""URLs for the instructors app."""
from django.urls import path

from . import views

app_name = 'instructors'

urlpatterns = [
    path('', views.InstructorListView.as_view(), name='list'),
    path('become/', views.BecomeInstructorView.as_view(), name='become'),
    path('dashboard/', views.InstructorDashboardView.as_view(), name='dashboard'),
    path('edit/', views.InstructorProfileEditView.as_view(), name='edit'),
    path('<slug:slug>/', views.InstructorDetailView.as_view(), name='detail'),
]
