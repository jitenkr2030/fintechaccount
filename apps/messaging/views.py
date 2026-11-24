"""Views for the messaging app."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, View, FormView

from apps.accounts.models import User
from .models import Thread, ThreadParticipant, Message
from .forms import MessageForm, NewThreadForm


def get_or_create_thread(user_a, user_b):
    """Find the 1:1 thread between two users, or create one."""
    existing = Thread.objects.filter(is_group=False, participants=user_a).filter(participants=user_b)
    if existing.exists():
        return existing.first()
    thread = Thread.objects.create(created_by=user_a)
    ThreadParticipant.objects.create(thread=thread, user=user_a)
    ThreadParticipant.objects.create(thread=thread, user=user_b)
    return thread


class InboxView(LoginRequiredMixin, ListView):
    """List of the user's conversations."""

    template_name = 'messaging/inbox.html'
    context_object_name = 'threads'
    paginate_by = 20

    def get_queryset(self):
        user = self.request.user
        qs = Thread.objects.filter(participants=user)
        return qs.order_by('-last_message_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'messages'
        # Unread counts per thread
        unread = {}
        for thread in ctx['threads']:
            membership = ThreadParticipant.objects.filter(
                thread=thread, user=self.request.user,
            ).first()
            last_read = membership.last_read_at if membership else None
            qs = thread.messages.all()
            if last_read:
                qs = qs.exclude(sender=self.request.user).filter(created_at__gt=last_read)
            else:
                qs = qs.exclude(sender=self.request.user)
            unread[thread.id] = qs.count()
        ctx['unread'] = unread
        return ctx


class ThreadDetailView(LoginRequiredMixin, DetailView):
    model = Thread
    template_name = 'messaging/thread_detail.html'
    context_object_name = 'thread'

    def dispatch(self, request, *args, **kwargs):
        thread = self.get_object()
        if not thread.participants.filter(id=request.user.id).exists():
            return HttpResponseForbidden('You are not part of this conversation.')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['messages'] = self.object.messages.select_related('sender').all()
        ctx['form'] = MessageForm()
        ctx['nav_active'] = 'messages'
        # Mark messages as read
        membership = ThreadParticipant.objects.filter(
            thread=self.object, user=self.request.user,
        ).first()
        if membership:
            membership.last_read_at = timezone.now()
            membership.save(update_fields=['last_read_at'])
        return ctx

    def post(self, request, *args, **kwargs):
        thread = self.get_object()
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            msg = Message.objects.create(
                thread=thread, sender=request.user,
                body=form.cleaned_data['body'],
                attachment=request.FILES.get('attachment'),
            )
            thread.last_message_at = msg.created_at
            thread.save(update_fields=['last_message_at'])
            messages.success(request, 'Message sent.')
        return redirect('messaging:thread_detail', pk=thread.pk)


class NewThreadView(LoginRequiredMixin, FormView):
    template_name = 'messaging/new_thread.html'
    form_class = NewThreadForm

    def form_valid(self, form):
        recipient = get_object_or_404(User, pk=form.cleaned_data['recipient'], is_active=True)
        if recipient == self.request.user:
            messages.error(self.request, 'You cannot message yourself.')
            return redirect('messaging:inbox')
        thread = get_or_create_thread(self.request.user, recipient)
        Message.objects.create(
            thread=thread, sender=self.request.user,
            body=form.cleaned_data['body'],
        )
        if form.cleaned_data.get('subject'):
            thread.subject = form.cleaned_data['subject']
            thread.save(update_fields=['subject'])
        return redirect('messaging:thread_detail', pk=thread.pk)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'messages'
        return ctx
