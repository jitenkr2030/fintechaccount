"""URLs for the communities app."""
from django.urls import path

from . import views

app_name = 'communities'

urlpatterns = [
    path('', views.CommunityListView.as_view(), name='list'),
    path('new/', views.CommunityCreateView.as_view(), name='create'),
    path('<slug:slug>/', views.CommunityDetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', views.CommunityUpdateView.as_view(), name='edit'),
    path('<slug:slug>/join/', views.JoinCommunityView.as_view(), name='join'),
    path('<slug:slug>/leave/', views.LeaveCommunityView.as_view(), name='leave'),
    path('<slug:slug>/topic/new/', views.TopicCreateView.as_view(), name='topic_create'),
    path('<slug:slug>/topic/<int:pk>/',
         views.TopicDetailView.as_view(), name='topic_detail'),
    path('<slug:slug>/topic/<int:pk>/reply/',
         views.ReplyCreateView.as_view(), name='reply_create'),
]
