"""Views for the payments app."""
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import View, TemplateView

from .models import Order, Subscription
from . import razorpay_client


# ---------------------------------------------------------------------------
# Price lookup helper (single source of truth for paid items)
# ---------------------------------------------------------------------------
PRICE_TABLE = {
    Order.COURSE: lambda obj: getattr(obj, 'effective_price', getattr(obj, 'price', 0)),
    Order.EVENT: lambda obj: getattr(obj, 'price', 0),
    Order.MEMBERSHIP: lambda obj: 299,  # ₹299/month premium membership (top of ₹99-299 range)
    Order.RECRUITER_SUB: lambda obj: 2999,  # ₹2,999/month recruiter subscription
    Order.JOB_FEATURED: lambda obj: 999,    # ₹999+ featured listing
    Order.CORPORATE_TRAINING: lambda obj: getattr(obj, 'price', 0),
}


def get_object_for_order(content_type, object_id):
    """Return the related object (Course/Event/Job etc.)."""
    if content_type == Order.COURSE:
        from apps.courses.models import Course
        return Course.objects.filter(pk=object_id).first()
    if content_type == Order.EVENT:
        from apps.events.models import Event
        return Event.objects.filter(pk=object_id).first()
    if content_type == Order.JOB_FEATURED:
        from apps.careers.models import Job
        return Job.objects.filter(pk=object_id).first()
    return None


# ---------------------------------------------------------------------------
# Checkout flow
# ---------------------------------------------------------------------------
class CheckoutView(LoginRequiredMixin, View):
    """Create an order at Razorpay and show the checkout page."""

    template_name = 'payments/checkout.html'

    def get(self, request, content_type, object_id):
        if content_type not in dict(Order.CONTENT_TYPES):
            return HttpResponseBadRequest('Invalid content type.')
        obj = get_object_for_order(content_type, object_id)
        if not obj:
            return HttpResponseBadRequest('Object not found.')

        amount = PRICE_TABLE[content_type](obj)
        amount = max(amount, 0)
        if not amount:
            # Free content -> just complete the action directly
            self._free_complete(request, content_type, object_id)
            return redirect(self._success_url(content_type, object_id))

        amount_paise = int(amount * 100)
        rp_order = razorpay_client.create_order(
            amount_paise,
            currency=settings.RAZORPAY_CURRENCY,
            receipt=f'{content_type}-{object_id}',
            notes={'user_id': request.user.id, 'content_type': content_type,
                   'object_id': object_id},
        )
        order = Order.objects.create(
            user=request.user,
            amount=amount,
            currency=settings.RAZORPAY_CURRENCY,
            content_type_label=content_type,
            object_id=object_id,
            description=f'{dict(Order.CONTENT_TYPES)[content_type]} #{object_id}',
            razorpay_order_id=rp_order.get('id', ''),
            status=Order.CREATED,
        )
        return render(request, self.template_name, {
            'order': order,
            'rp_order_id': rp_order.get('id', ''),
            'rp_key_id': settings.RAZORPAY_KEY_ID or 'mock_key',
            'amount_paise': amount_paise,
            'currency': settings.RAZORPAY_CURRENCY,
            'rp_mock': not razorpay_client.is_configured(),
            'nav_active': 'payments',
        })

    def _success_url(self, content_type, object_id):
        if content_type == Order.COURSE:
            return reverse('courses:learn', kwargs={'slug': get_object_for_order(content_type, object_id).slug})
        if content_type == Order.EVENT:
            return reverse('events:detail', kwargs={'slug': get_object_for_order(content_type, object_id).slug})
        return '/dashboard/'

    def _free_complete(self, request, content_type, object_id):
        if content_type == Order.COURSE:
            from apps.courses.models import Course, Enrollment
            course = Course.objects.filter(pk=object_id).first()
            if course:
                enrollment, created = Enrollment.objects.get_or_create(
                    course=course, student=request.user,
                    defaults={'status': Enrollment.ACTIVE},
                )
                if created:
                    course.students_count += 1
                    course.save(update_fields=['students_count'])


class VerifyPaymentView(LoginRequiredMixin, View):
    """Verify the Razorpay payment after checkout."""

    def post(self, request, order_id):
        order = get_object_or_404(Order, razorpay_order_id=order_id, user=request.user)
        payment_id = request.POST.get('razorpay_payment_id', '').strip()
        signature = request.POST.get('razorpay_signature', '').strip()

        # Mock-mode shortcut
        if order.razorpay_order_id.startswith('mock_') and payment_id and not signature:
            signature = 'mock_signature'

        if not (payment_id and signature):
            return JsonResponse({'status': 'failed', 'detail': 'Missing payment fields.'},
                                 status=400)

        ok = razorpay_client.verify_payment(order.razorpay_order_id, payment_id, signature)
        if not ok:
            order.status = Order.FAILED
            order.save(update_fields=['status'])
            messages.error(request, 'Payment verification failed.')
            return JsonResponse({'status': 'failed'})

        order.status = Order.PAID
        order.razorpay_payment_id = payment_id
        order.razorpay_signature = signature
        order.paid_at = timezone.now()
        order.save(update_fields=['status', 'razorpay_payment_id',
                                   'razorpay_signature', 'paid_at'])

        # Fulfil the order (activate enrollment / registration / featured job etc.)
        self._fulfil(order)
        return JsonResponse({'status': 'paid',
                              'redirect': self._success_url(order)})

    def _success_url(self, order):
        if order.content_type_label == Order.COURSE:
            from apps.courses.models import Course
            course = Course.objects.filter(pk=order.object_id).first()
            if course:
                return reverse('courses:learn', kwargs={'slug': course.slug})
        return '/dashboard/'

    def _fulfil(self, order):
        """Activate the entitlement paid for."""
        if order.content_type_label == Order.COURSE:
            from apps.courses.models import Course, Enrollment
            course = Course.objects.filter(pk=order.object_id).first()
            if course:
                enrollment, created = Enrollment.objects.get_or_create(
                    course=course, student=order.user,
                    defaults={'status': Enrollment.ACTIVE},
                )
                if created:
                    course.students_count += 1
                    course.save(update_fields=['students_count'])
        elif order.content_type_label == Order.EVENT:
            from apps.events.models import Event, EventRegistration
            event = Event.objects.filter(pk=order.object_id).first()
            if event:
                EventRegistration.objects.get_or_create(event=event, user=order.user)
                event.registrations_count += 1
                event.save(update_fields=['registrations_count'])
        elif order.content_type_label == Order.MEMBERSHIP:
            order.user.is_premium = True
            order.user.save(update_fields=['is_premium'])
            self._ensure_subscription(order, Subscription.PREMIUM_MEMBER)
        elif order.content_type_label == Order.RECRUITER_SUB:
            self._ensure_subscription(order, Subscription.RECRUITER)
        elif order.content_type_label == Order.JOB_FEATURED:
            from apps.careers.models import Job
            job = Job.objects.filter(pk=order.object_id).first()
            if job:
                job.is_featured = True
                job.save(update_fields=['is_featured'])

    def _ensure_subscription(self, order, sub_type):
        from datetime import timedelta
        sub, created = Subscription.objects.get_or_create(
            user=order.user, subscription_type=sub_type, status=Subscription.ACTIVE,
            defaults={
                'amount': order.amount,
                'billing_cycle_days': 30,
                'current_period_end': timezone.now() + timedelta(days=30),
            },
        )
        if not created:
            # Extend existing
            sub.current_period_end = max(sub.current_period_end, timezone.now()) + timedelta(days=30)
            sub.save(update_fields=['current_period_end'])


class PaymentHistoryView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/history.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['orders'] = Order.objects.filter(user=self.request.user)
        ctx['subscriptions'] = Subscription.objects.filter(user=self.request.user)
        ctx['nav_active'] = 'payments'
        return ctx
