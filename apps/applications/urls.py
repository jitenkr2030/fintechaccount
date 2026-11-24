"""URLs for the applications app."""
from django.urls import path

from . import views

app_name = 'applications'

urlpatterns = [
    path('apply/<slug:slug>/', views.ApplyView.as_view(), name='apply'),
    path('my/', views.MyApplicationsView.as_view(), name='my_list'),
    path('<int:pk>/', views.ApplicationDetailView.as_view(), name='my_detail'),
    path('<int:pk>/withdraw/', views.WithdrawApplicationView.as_view(), name='withdraw'),
    path('<int:pk>/status/', views.UpdateApplicationStatusView.as_view(), name='update_status'),
    path('<int:pk>/notes/', views.UpdateApplicationNotesView.as_view(), name='update_notes'),
    path('job/<slug:slug>/', views.JobApplicationsView.as_view(), name='job_applications'),
]
