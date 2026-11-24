"""DRF API views for the payments app."""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from django.utils import timezone

from .models import Order, Subscription
from . import razorpay_client
from .serializers import OrderSerializer, SubscriptionSerializer


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'content_type_label']

    def get_queryset(self):
        qs = Order.objects.select_related('user')
        if self.request.user.is_admin_role:
            return qs
        return qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        # API order creation: create a Razorpay order and store its id
        amount = serializer.validated_data['amount']
        rp_order = razorpay_client.create_order(
            int(amount * 100),
            currency=settings.RAZORPAY_CURRENCY,
            receipt=f'api-{self.request.user.id}',
        )
        serializer.save(
            user=self.request.user,
            razorpay_order_id=rp_order.get('id', ''),
        )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def verify(self, request, pk=None):
        order = self.get_object()
        if order.user_id != request.user.id and not request.user.is_admin_role:
            return Response({'detail': 'Not allowed.'},
                            status=status.HTTP_403_FORBIDDEN)
        payment_id = request.data.get('razorpay_payment_id', '').strip()
        signature = request.data.get('razorpay_signature', '').strip()
        if order.razorpay_order_id.startswith('mock_') and payment_id and not signature:
            signature = 'mock_signature'
        ok = razorpay_client.verify_payment(order.razorpay_order_id, payment_id, signature)
        if not ok:
            order.status = Order.FAILED
            order.save(update_fields=['status'])
            return Response({'status': 'failed'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = Order.PAID
        order.razorpay_payment_id = payment_id
        order.razorpay_signature = signature
        order.paid_at = timezone.now()
        order.save(update_fields=['status', 'razorpay_payment_id',
                                   'razorpay_signature', 'paid_at'])
        return Response(OrderSerializer(order).data)


class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['subscription_type', 'status']

    def get_queryset(self):
        qs = Subscription.objects.select_related('user')
        if self.request.user.is_admin_role:
            return qs
        return qs.filter(user=self.request.user)
