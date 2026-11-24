"""URLs for the accounts app - Phase 1 (auth, profile, directory)."""
from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('me/', views.MyProfileView.as_view(), name='my_profile'),
    path('me/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('me/roles/', views.RoleEditView.as_view(), name='role_edit'),

    path('directory/', views.DirectoryView.as_view(), name='directory'),
]
