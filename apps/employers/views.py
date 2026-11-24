"""Views for the employers app."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, UpdateView, View, TemplateView,
)

from apps.accounts.models import User, Role
from apps.profiles.models import Profile
from .models import EmployerProfile
from .forms import EmployerProfileForm, BecomeEmployerForm


class EmployerListView(ListView):
    model = EmployerProfile
    template_name = 'employers/employer_list.html'
    context_object_name = 'employers'
    paginate_by = 12

    def get_queryset(self):
        qs = EmployerProfile.objects.select_related('user')
        q = self.request.GET.get('q')
        industry = self.request.GET.get('industry')
        if q:
            qs = qs.filter(
                Q(company_name__icontains=q) | Q(about__icontains=q)
                | Q(headquarters_city__icontains=q)
            )
        if industry:
            qs = qs.filter(industry__icontains=industry)
        return qs.order_by('-is_verified', 'company_name')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'employers'
        return ctx


class EmployerDetailView(DetailView):
    model = EmployerProfile
    template_name = 'employers/employer_detail.html'
    context_object_name = 'employer'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'employers'
        ctx['jobs'] = self.object.jobs.filter(status='open')[:10]
        return ctx


class BecomeEmployerView(LoginRequiredMixin, View):
    template_name = 'employers/become_employer.html'

    def get(self, request, *args, **kwargs):
        if hasattr(request.user, 'employer_profile'):
            return redirect('employers:dashboard')
        form = BecomeEmployerForm()
        return self._render(request, form)

    def post(self, request, *args, **kwargs):
        form = BecomeEmployerForm(request.POST)
        if form.is_valid():
            request.user.add_role(Role.EMPLOYER)
            profile = EmployerProfile.objects.create(
                user=request.user,
                company_name=form.cleaned_data['company_name'],
                industry=form.cleaned_data.get('industry', ''),
                headquarters_city=form.cleaned_data.get('headquarters_city', ''),
                contact_email=form.cleaned_data.get('contact_email', '') or request.user.email,
            )
            messages.success(request, 'Employer profile created!')
            return redirect('employers:edit')
        return self._render(request, form)

    def _render(self, request, form):
        return render(request, self.template_name,
                      {'form': form, 'nav_active': 'employers'})


class EmployerProfileEditView(LoginRequiredMixin, UpdateView):
    model = EmployerProfile
    form_class = EmployerProfileForm
    template_name = 'employers/employer_edit.html'
    success_url = reverse_lazy('employers:dashboard')

    def get_object(self, queryset=None):
        return get_object_or_404(EmployerProfile, user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Company profile updated.')
        return super().form_valid(form)


class EmployerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'employers/dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_employer and not request.user.is_admin_role:
            return HttpResponseForbidden('Employers only.')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'employers'
        profile = getattr(self.request.user, 'employer_profile', None)
        if profile:
            ctx['employer'] = profile
            ctx['jobs'] = profile.jobs.all().order_by('-posted_at')[:5]
            from apps.applications.models import JobApplication
            ctx['recent_applications'] = JobApplication.objects.filter(
                job__employer=profile,
            ).select_related('applicant', 'job').order_by('-applied_at')[:10]
        else:
            ctx['employer'] = None
            ctx['jobs'] = []
            ctx['recent_applications'] = []
        return ctx


class CandidateSearchView(LoginRequiredMixin, ListView):
    """Search candidate profiles (employer only)."""

    template_name = 'employers/candidate_search.html'
    context_object_name = 'profiles'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_employer and not request.user.is_admin_role:
            return HttpResponseForbidden('Employers only.')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = Profile.objects.filter(
            user__is_active=True, is_open_to_work=True,
        ).select_related('user')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q)
                | Q(current_title__icontains=q) | Q(industry__icontains=q)
                | Q(user__headline__icontains=q)
            )
        return qs.distinct()[:50]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'employers'
        ctx['q'] = self.request.GET.get('q', '')
        return ctx
