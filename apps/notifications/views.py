"""Views for the notifications app."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, View, TemplateView

from .models import Notification, Announcement


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 30

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'notifications'
        ctx['unread_count'] = Notification.objects.filter(
            recipient=self.request.user, is_read=False,
        ).count()
        ctx['announcements'] = Announcement.objects.filter(
            is_published=True,
        )[:5]
        return ctx


class MarkReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notif.is_read = True
        notif.save(update_fields=['is_read'])
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'read': True})
        return redirect('notifications:list')


class MarkAllReadView(LoginRequiredMixin, View):
    def post(self, request):
        Notification.objects.filter(
            recipient=request.user, is_read=False,
        ).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('notifications:list')


class UnreadCountView(LoginRequiredMixin, View):
    """AJAX endpoint used by the navbar bell badge."""

    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user, is_read=False,
        ).count()
        return JsonResponse({'unread': count})
