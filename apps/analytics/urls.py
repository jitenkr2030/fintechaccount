from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.MyInsightsView.as_view(), name='my_insights'),
    path('admin/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
]
