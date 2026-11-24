"""Views for the moderation app."""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, View, TemplateView,
)

from .models import Report, ModerationAction
from .forms import ReportForm, ModerationActionForm


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_admin_role


class ReportCreateView(LoginRequiredMixin, CreateView):
    """Any logged-in user can report content."""

    model = Report
    form_class = ReportForm
    template_name = 'moderation/report_form.html'
    success_url = reverse_lazy('moderation:my_reports')

    def form_valid(self, form):
        report = form.save(commit=False)
        report.reporter = self.request.user
        report.save()
        messages.success(self.request, 'Thank you. Your report has been submitted.')
        return super().form_valid(form)


class MyReportsView(LoginRequiredMixin, ListView):
    template_name = 'moderation/my_reports.html'
    context_object_name = 'reports'

    def get_queryset(self):
        return Report.objects.filter(reporter=self.request.user).order_by('-created_at')


class ReportQueueView(AdminRequiredMixin, ListView):
    """Admin moderation queue."""

    template_name = 'moderation/queue.html'
    context_object_name = 'reports'
    paginate_by = 30

    def get_queryset(self):
        qs = Report.objects.select_related('reporter', 'assigned_to')
        status = self.request.GET.get('status')
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('status', '-created_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['statuses'] = Report.STATUSES
        ctx['selected_status'] = self.request.GET.get('status', '')
        ctx['pending_count'] = Report.objects.filter(status=Report.PENDING).count()
        return ctx


class ReportDetailView(AdminRequiredMixin, DetailView):
    model = Report
    template_name = 'moderation/report_detail.html'
    context_object_name = 'report'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['actions'] = self.object.actions.all()
        ctx['action_form'] = ModerationActionForm()
        return ctx


class TakeActionView(AdminRequiredMixin, View):
    """Admin takes an action on a report."""

    def post(self, request, pk):
        report = get_object_or_404(Report, pk=pk)
        form = ModerationActionForm(request.POST)
        if form.is_valid():
            action = form.save(commit=False)
            action.report = report
            action.admin = request.user
            action.save()
            # Update report status based on action
            new_status = Report.RESOLVED if action.action != ModerationAction.NO_ACTION \
                else Report.DISMISSED
            report.status = new_status
            report.assigned_to = request.user
            report.resolution_notes = form.cleaned_data['notes']
            report.save(update_fields=['status', 'assigned_to', 'resolution_notes', 'updated_at'])
            messages.success(request, f'Action "{action.get_action_display()}" taken.')
        return redirect('moderation:report_detail', pk=report.pk)
