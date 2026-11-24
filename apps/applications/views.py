"""Views for the applications app."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView,
)

from apps.careers.models import Job
from .models import JobApplication
from .forms import ApplicationForm


class ApplyView(LoginRequiredMixin, CreateView):
    """Apply for a job."""

    model = JobApplication
    form_class = ApplicationForm
    template_name = 'applications/apply.html'

    def dispatch(self, request, *args, **kwargs):
        self.job = get_object_or_404(Job, slug=kwargs['slug'], status=Job.OPEN)
        existing = JobApplication.objects.filter(job=self.job, applicant=request.user).first()
        if existing:
            messages.info(request, 'You have already applied for this job.')
            return redirect('applications:my_detail', pk=existing.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        application = form.save(commit=False)
        application.job = self.job
        application.applicant = self.request.user
        # Fall back to profile resume if not provided
        if not application.resume and hasattr(self.request.user, 'profile'):
            application.resume = self.request.user.profile.resume
        application.save()
        messages.success(self.request, 'Application submitted!')
        return redirect('applications:my_detail', pk=application.pk)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['job'] = self.job
        ctx['nav_active'] = 'careers'
        return ctx


class MyApplicationsView(LoginRequiredMixin, ListView):
    """List the current user's job applications."""

    template_name = 'applications/my_applications.html'
    context_object_name = 'applications'

    def get_queryset(self):
        return JobApplication.objects.filter(
            applicant=self.request.user,
        ).select_related('job', 'job__employer').order_by('-applied_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'applications'
        return ctx


class ApplicationDetailView(LoginRequiredMixin, DetailView):
    model = JobApplication
    template_name = 'applications/application_detail.html'
    context_object_name = 'application'

    def dispatch(self, request, *args, **kwargs):
        app = self.get_object()
        is_applicant = app.applicant_id == request.user.id
        is_owner = app.job.posted_by_id == request.user.id
        is_admin = request.user.is_admin_role
        if not (is_applicant or is_owner or is_admin):
            return HttpResponseForbidden('Not allowed to view this application.')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['is_applicant'] = self.object.applicant_id == self.request.user.id
        ctx['is_employer'] = self.object.job.posted_by_id == self.request.user.id
        return ctx


class WithdrawApplicationView(LoginRequiredMixin, View):
    def post(self, request, pk):
        app = get_object_or_404(JobApplication, pk=pk, applicant=request.user)
        app.status = JobApplication.WITHDRAWN
        app.save(update_fields=['status', 'updated_at'])
        messages.info(request, 'Application withdrawn.')
        return redirect('applications:my_list')


# ---------------------------------------------------------------------------
# Employer-side: view all applications for a job, update status, shortlist
# ---------------------------------------------------------------------------
class JobApplicationsView(LoginRequiredMixin, ListView):
    """List applications for one job (employer only)."""

    template_name = 'applications/job_applications.html'
    context_object_name = 'applications'

    def dispatch(self, request, *args, **kwargs):
        self.job = get_object_or_404(Job, slug=kwargs['slug'])
        if self.job.posted_by_id != request.user.id and not request.user.is_admin_role:
            return HttpResponseForbidden('Only the employer can view applications.')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return JobApplication.objects.filter(
            job=self.job,
        ).exclude(status=JobApplication.WITHDRAWN).select_related(
            'applicant', 'applicant__profile',
        ).order_by('-applied_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['job'] = self.job
        ctx['statuses'] = JobApplication.STATUSES
        return ctx


class UpdateApplicationStatusView(LoginRequiredMixin, View):
    """Employer updates the status of an application (shortlist/reject/etc.)."""

    def post(self, request, pk):
        app = get_object_or_404(JobApplication, pk=pk)
        if app.job.posted_by_id != request.user.id and not request.user.is_admin_role:
            return HttpResponseForbidden('Only the employer can update status.')
        new_status = request.POST.get('status')
        valid = {s for s, _ in JobApplication.STATUSES}
        if new_status in valid:
            app.status = new_status
            app.save(update_fields=['status', 'updated_at'])
            messages.success(request, f'Application marked as {new_status}.')
        return redirect('applications:job_applications', slug=app.job.slug)


class UpdateApplicationNotesView(LoginRequiredMixin, View):
    """Employer updates internal notes / rating on an application."""

    def post(self, request, pk):
        app = get_object_or_404(JobApplication, pk=pk)
        if app.job.posted_by_id != request.user.id and not request.user.is_admin_role:
            return HttpResponseForbidden('Only the employer can update notes.')
        app.employer_notes = request.POST.get('employer_notes', '')
        rating = request.POST.get('rating', '0')
        try:
            app.rating = max(0, min(5, int(rating)))
        except ValueError:
            app.rating = 0
        app.save(update_fields=['employer_notes', 'rating', 'updated_at'])
        messages.success(request, 'Notes saved.')
        return redirect('applications:detail', pk=app.pk)
