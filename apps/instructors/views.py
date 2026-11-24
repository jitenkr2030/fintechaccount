"""Views for the instructors app."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, DetailView, UpdateView, TemplateView,
)

from apps.accounts.models import Role
from apps.courses.models import Course, Enrollment
from .models import InstructorProfile, Payout
from .forms import InstructorProfileForm


class InstructorListView(ListView):
    model = InstructorProfile
    template_name = 'instructors/instructor_list.html'
    context_object_name = 'instructors'
    paginate_by = 12

    def get_queryset(self):
        qs = InstructorProfile.objects.select_related('user')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                title__icontains=q,
            ) | qs.filter(expertise__icontains=q) \
              | qs.filter(bio__icontains=q)
        return qs.order_by('-is_verified', '-students_count')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'instructors'
        return ctx


class InstructorDetailView(DetailView):
    model = InstructorProfile
    template_name = 'instructors/instructor_detail.html'
    context_object_name = 'instructor'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'instructors'
        ctx['courses'] = self.object.user.courses_taught.filter(
            status=Course.PUBLISHED,
        ).order_by('-students_count')
        return ctx


class BecomeInstructorView(LoginRequiredMixin, TemplateView):
    """Self-onboard as an instructor."""

    template_name = 'instructors/become_instructor.html'

    def get(self, request, *args, **kwargs):
        if not hasattr(request.user, 'instructor_profile'):
            return super().get(request, *args, **kwargs)
        return redirect('instructors:dashboard')

    def post(self, request, *args, **kwargs):
        # Grant role
        request.user.add_role(Role.INSTRUCTOR)
        # Create instructor profile from form fields
        profile = InstructorProfile.objects.create(
            user=request.user,
            title=request.POST.get('title', 'New Instructor'),
            bio=request.POST.get('bio', ''),
            expertise=request.POST.get('expertise', ''),
        )
        messages.success(request, 'You are now an instructor!')
        return redirect('instructors:edit')


class InstructorProfileEditView(LoginRequiredMixin, UpdateView):
    model = InstructorProfile
    form_class = InstructorProfileForm
    template_name = 'instructors/instructor_edit.html'
    success_url = reverse_lazy('instructors:dashboard')

    def get_object(self, queryset=None):
        if not hasattr(self.request.user, 'instructor_profile'):
            return HttpResponseForbidden('You are not an instructor yet.')
        return self.request.user.instructor_profile

    def form_valid(self, form):
        messages.success(self.request, 'Instructor profile updated.')
        return super().form_valid(form)


class InstructorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'instructors/dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_instructor and not request.user.is_admin_role:
            return HttpResponseForbidden('Instructors only.')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'instructors'
        profile = getattr(self.request.user, 'instructor_profile', None)
        ctx['profile'] = profile
        if profile:
            ctx['courses'] = profile.user.courses_taught.all().order_by('-created_at')[:10]
            ctx['payouts'] = profile.payouts.all()[:5]
            ctx['total_students'] = (
                Enrollment.objects.filter(course__instructor=profile.user).count()
            )
            ctx['pending_payout'] = profile.payouts.filter(
                status=Payout.PENDING,
            ).aggregate(total=Sum('amount'))['total'] or 0
        else:
            ctx['courses'] = []
            ctx['payouts'] = []
            ctx['total_students'] = 0
            ctx['pending_payout'] = 0
        return ctx
