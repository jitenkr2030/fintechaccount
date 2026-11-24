"""URLs for the profiles app."""
from django.urls import path

from . import views

app_name = 'profiles'

urlpatterns = [
    path('u/<slug:slug>/', views.ProfileDetailView.as_view(), name='detail'),
    path('me/edit/', views.MyProfileEditView.as_view(), name='my_edit'),
    path('me/section/<str:section>/add/', views.ProfileSectionCreateView.as_view(),
         name='section_add'),
    path('me/section/<str:section>/<int:pk>/delete/',
         views.ProfileSectionDeleteView.as_view(), name='section_delete'),
    path('me/resume/', views.ResumeView.as_view(), name='resume'),
]
