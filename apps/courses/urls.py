"""URLs for the courses app."""
from django.urls import path

from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='list'),
    path('categories/', views.CategoryListView.as_view(), name='categories'),
    path('my/', views.MyCoursesView.as_view(), name='my_courses'),
    path('new/', views.CourseCreateView.as_view(), name='create'),

    path('<slug:slug>/', views.CourseDetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', views.CourseUpdateView.as_view(), name='edit'),
    path('<slug:slug>/enroll/', views.EnrollView.as_view(), name='enroll'),
    path('<slug:slug>/review/', views.ReviewCreateView.as_view(), name='review_create'),
    path('<slug:slug>/learn/', views.LearnView.as_view(), name='learn'),

    path('<slug:slug>/lesson/<int:pk>/', views.LessonView.as_view(), name='lesson'),
    path('<slug:slug>/lesson/<int:pk>/complete/',
         views.MarkLessonCompleteView.as_view(), name='lesson_complete'),
]
