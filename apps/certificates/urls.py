"""URLs for the certificates app."""
from django.urls import path

from . import views

app_name = 'certificates'

urlpatterns = [
    path('my/', views.MyCertificatesView.as_view(), name='my_certificates'),
    path('verify/', views.VerifyCertificateView.as_view(), name='verify'),
    path('view/<str:certificate_id>/', views.CertificateDetailView.as_view(), name='detail'),
    path('download/<str:certificate_id>/', views.CertificateDownloadView.as_view(),
         name='download'),
]
