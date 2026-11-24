"""Views for the events app."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View,
)

from .models import Event, EventRegistration
from .forms import EventForm


class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 12

    def get_queryset(self):
        qs = Event.objects.filter(status=Event.PUBLISHED)
        q = self.request.GET.get('q')
        event_type = self.request.GET.get('event_type')
        upcoming = self.request.GET.get('upcoming')
        if q:
            qs = qs.filter(
                Q(title__icontains=q) | Q(description__icontains=q)
                | Q(city__icontains=q) | Q(venue__icontains=q)
            )
        if event_type:
            qs = qs.filter(event_type=event_type)
        if upcoming == '1':
            qs = qs.filter(starts_at__gt=timezone.now())
        return qs.order_by('-is_featured', '-starts_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'events'
        ctx['event_types'] = Event.TYPES
        ctx['selected_type'] = self.request.GET.get('event_type', '')
        ctx['q'] = self.request.GET.get('q', '')
        ctx['upcoming'] = self.request.GET.get('upcoming', '')
        return ctx


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'events'
        if self.request.user.is_authenticated:
            ctx['is_registered'] = EventRegistration.objects.filter(
                event=self.object, user=self.request.user,
            ).exists()
        else:
            ctx['is_registered'] = False
        return ctx


class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'

    def form_valid(self, form):
        event = form.save(commit=False)
        event.organiser = self.request.user
        event.save()
        messages.success(self.request, f'Event "{event.title}" created.')
        return redirect('events:detail', slug=event.slug)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'events'
        return ctx


class EventUpdateView(LoginRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'

    def dispatch(self, request, *args, **kwargs):
        event = self.get_object()
        if event.organiser_id != request.user.id and not request.user.is_admin_role:
            return HttpResponseForbidden('Only the organiser can edit this event.')
        return super().dispatch(request, *args, **kwargs)


class EventRegisterView(LoginRequiredMixin, View):
    def post(self, request, slug):
        event = get_object_or_404(Event, slug=slug, status=Event.PUBLISHED)
        reg, created = EventRegistration.objects.get_or_create(
            event=event, user=request.user,
        )
        if created:
            event.registrations_count += 1
            event.save(update_fields=['registrations_count'])
            messages.success(request, f'Registered for "{event.title}".')
        else:
            messages.info(request, 'You are already registered.')
        return redirect('events:detail', slug=slug)


class MyEventsView(LoginRequiredMixin, ListView):
    template_name = 'events/my_events.html'
    context_object_name = 'events'

    def get_queryset(self):
        return Event.objects.filter(
            registrations__user=self.request.user,
        ).order_by('-starts_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'events'
        return ctx
