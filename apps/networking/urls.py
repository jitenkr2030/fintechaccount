"""URLs for the networking app."""
from django.urls import path

from . import views

app_name = 'networking'

urlpatterns = [
    path('', views.FeedView.as_view(), name='feed'),
    path('post/new/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('post/<int:pk>/like/', views.LikeToggleView.as_view(), name='post_like'),
    path('post/<int:pk>/comment/', views.CommentCreateView.as_view(), name='comment_create'),

    path('connections/', views.ConnectionsView.as_view(), name='connections'),
    path('connect/<int:user_id>/', views.ConnectionToggleView.as_view(), name='connect_toggle'),
    path('connection/<int:pk>/<str:action>/',
         views.ConnectionActionView.as_view(), name='connection_action'),
]
