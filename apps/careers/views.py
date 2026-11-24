"""Views for the careers app - jobs list, detail, post, alerts."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView,
    FormView,
)

from apps.employers.models import EmployerProfile
from .models import Job, JobCategory, JobAlert
from .forms import JobForm, JobSearchForm, JobAlertForm


class JobListView(ListView):
    model = Job
    template_name = 'careers/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 15

    def get_queryset(self):
        qs = Job.objects.filter(status=Job.OPEN)
        q = self.request.GET.get('q')
        category = self.request.GET.get('category')
        location = self.request.GET.get('location')
        employment_type = self.request.GET.get('employment_type')
        is_remote = self.request.GET.get('is_remote')

        if q:
            qs = qs.filter(
                Q(title__icontains=q) | Q(description__icontains=q)
                | Q(skills_required__icontains=q)
                | Q(employer__company_name__icontains=q)
            )
        if category:
            qs = qs.filter(category__slug=category)
        if location:
            qs = qs.filter(
                Q(location_city__icontains=location) | Q(location_state__icontains=location)
            )
        if employment_type:
            qs = qs.filter(employment_type=employment_type)
        if is_remote == '1':
            qs = qs.filter(is_remote=True)
        # Hide expired
        qs = qs.exclude(application_deadline__lt=timezone.now())
        return qs.order_by('-is_featured', '-posted_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'careers'
        ctx['categories'] = JobCategory.objects.all()
        ctx['employment_types'] = Job.EMPLOYMENT_TYPES
        ctx['selected_category'] = self.request.GET.get('category', '')
        ctx['selected_type'] = self.request.GET.get('employment_type', '')
        ctx['q'] = self.request.GET.get('q', '')
        ctx['search_form'] = JobSearchForm(self.request.GET)
        return ctx


class JobDetailView(DetailView):
    model = Job
    template_name = 'careers/job_detail.html'
    context_object_name = 'job'

    def get_queryset(self):
        return Job.objects.exclude(status=Job.DRAFT).select_related('employer', 'category')

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        # Increment views (cheap update)
        Job.objects.filter(pk=self.object.pk).update(views_count=self.object.views_count + 1)
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'careers'
        if self.request.user.is_authenticated:
            from apps.applications.models import JobApplication
            ctx['user_application'] = JobApplication.objects.filter(
                job=self.object, applicant=self.request.user,
            ).first()
        else:
            ctx['user_application'] = None
        return ctx


class JobCreateView(LoginRequiredMixin, CreateView):
    model = Job
    form_class = JobForm
    template_name = 'careers/job_form.html'

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_employer or request.user.is_admin_role):
            return HttpResponseForbidden('Only employers can post jobs.')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        job = form.save(commit=False)
        job.posted_by = self.request.user
        # Link to employer profile if exists
        employer = getattr(self.request.user, 'employer_profile', None)
        if employer:
            job.employer = employer
        job.save()
        messages.success(self.request, f'Job "{job.title}" posted.')
        return redirect('careers:detail', slug=job.slug)


class JobUpdateView(LoginRequiredMixin, UpdateView):
    model = Job
    form_class = JobForm
    template_name = 'careers/job_form.html'

    def dispatch(self, request, *args, **kwargs):
        job = self.get_object()
        if job.posted_by_id != request.user.id and not request.user.is_admin_role:
            return HttpResponseForbidden('Only the poster can edit this job.')
        return super().dispatch(request, *args, **kwargs)


class JobDeleteView(LoginRequiredMixin, DeleteView):
    model = Job
    template_name = 'careers/job_confirm_delete.html'
    success_url = reverse_lazy('careers:employer_jobs')

    def dispatch(self, request, *args, **kwargs):
        job = self.get_object()
        if job.posted_by_id != request.user.id and not request.user.is_admin_role:
            return HttpResponseForbidden('Only the poster can delete this job.')
        return super().dispatch(request, *args, **kwargs)


class EmployerJobsView(LoginRequiredMixin, ListView):
    """Jobs posted by the current user (employer dashboard)."""

    template_name = 'careers/employer_jobs.html'
    context_object_name = 'jobs'

    def get_queryset(self):
        return Job.objects.filter(posted_by=self.request.user).order_by('-posted_at')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'careers'
        return ctx


# ---------------------------------------------------------------------------
# Job alerts
# ---------------------------------------------------------------------------
class JobAlertCreateView(LoginRequiredMixin, CreateView):
    model = JobAlert
    form_class = JobAlertForm
    template_name = 'careers/job_alert_form.html'
    success_url = reverse_lazy('careers:my_alerts')

    def form_valid(self, form):
        alert = form.save(commit=False)
        alert.user = self.request.user
        alert.save()
        messages.success(self.request, 'Job alert created.')
        return super().form_valid(form)


class MyAlertsView(LoginRequiredMixin, ListView):
    template_name = 'careers/my_alerts.html'
    context_object_name = 'alerts'

    def get_queryset(self):
        return JobAlert.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'careers'
        return ctx


class AlertToggleView(LoginRequiredMixin, View):
    def post(self, request, pk):
        alert = get_object_or_404(JobAlert, pk=pk, user=request.user)
        alert.is_active = not alert.is_active
        alert.save(update_fields=['is_active'])
        return redirect('careers:my_alerts')
