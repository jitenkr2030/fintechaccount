"""URLs for the events app."""
from django.urls import path

from . import views

app_name = 'events'

urlpatterns = [
    path('', views.EventListView.as_view(), name='list'),
    path('new/', views.EventCreateView.as_view(), name='create'),
    path('my/', views.MyEventsView.as_view(), name='my_events'),
    path('<slug:slug>/', views.EventDetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', views.EventUpdateView.as_view(), name='edit'),
    path('<slug:slug>/register/', views.EventRegisterView.as_view(), name='register'),
]
