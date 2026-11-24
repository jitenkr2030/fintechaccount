"""URLs for the moderation app."""
from django.urls import path

from . import views

app_name = 'moderation'

urlpatterns = [
    path('report/', views.ReportCreateView.as_view(), name='report_create'),
    path('my-reports/', views.MyReportsView.as_view(), name='my_reports'),
    path('queue/', views.ReportQueueView.as_view(), name='queue'),
    path('<int:pk>/', views.ReportDetailView.as_view(), name='report_detail'),
    path('<int:pk>/action/', views.TakeActionView.as_view(), name='take_action'),
]
