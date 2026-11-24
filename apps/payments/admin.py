"""Admin for the payments app."""
from django.contrib import admin

from .models import Order, Subscription


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'currency', 'content_type_label',
                    'object_id', 'status', 'razorpay_order_id', 'created_at', 'paid_at')
    list_filter = ('status', 'content_type_label', 'currency')
    search_fields = ('user__email', 'razorpay_order_id', 'razorpay_payment_id', 'reference')
    readonly_fields = ('reference', 'razorpay_order_id', 'razorpay_payment_id',
                       'razorpay_signature', 'paid_at', 'created_at')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_type', 'amount', 'billing_cycle_days',
                    'status', 'current_period_end')
    list_filter = ('subscription_type', 'status')
    search_fields = ('user__email', 'razorpay_subscription_id')
    readonly_fields = ('started_at', 'current_period_end', 'cancelled_at')
