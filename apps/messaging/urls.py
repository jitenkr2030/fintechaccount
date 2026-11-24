"""URLs for the messaging app."""
from django.urls import path

from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.InboxView.as_view(), name='inbox'),
    path('thread/<int:pk>/', views.ThreadDetailView.as_view(), name='thread_detail'),
    path('new/', views.NewThreadView.as_view(), name='new_thread'),
]
