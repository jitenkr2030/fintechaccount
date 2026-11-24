"""DRF serializers for the payments app."""
from rest_framework import serializers

from .models import Order, Subscription


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'amount', 'currency', 'content_type_label',
                  'object_id', 'description', 'razorpay_order_id',
                  'razorpay_payment_id', 'status', 'reference',
                  'created_at', 'paid_at']
        read_only_fields = ['user', 'razorpay_order_id', 'razorpay_payment_id',
                             'razorpay_signature', 'status', 'reference',
                             'created_at', 'paid_at']


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'subscription_type', 'amount',
                  'billing_cycle_days', 'status', 'started_at',
                  'current_period_end', 'cancelled_at']
        read_only_fields = ['user', 'started_at', 'current_period_end',
                            'cancelled_at']
