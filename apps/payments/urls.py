"""URLs for the payments app."""
from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<str:content_type>/<int:object_id>/',
         views.CheckoutView.as_view(), name='checkout'),
    path('verify/<str:order_id>/', views.VerifyPaymentView.as_view(), name='verify'),
    path('history/', views.PaymentHistoryView.as_view(), name='history'),
]
