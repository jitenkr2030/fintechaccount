"""Views for the analytics app - dashboards and recommendations."""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.views.generic import TemplateView

from .models import Recommendation, UserActivity
from .recommenders import recommend_courses, recommend_jobs


class MyInsightsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/my_insights.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nav_active'] = 'analytics'
        recommend_courses(self.request.user)
        recommend_jobs(self.request.user)
        ctx['course_recs'] = Recommendation.objects.filter(
            user=self.request.user, source=Recommendation.LEARNING,
            is_dismissed=False,
        )[:5]
        ctx['job_recs'] = Recommendation.objects.filter(
            user=self.request.user, source=Recommendation.CAREER,
            is_dismissed=False,
        )[:5]
        ctx['activities'] = UserActivity.objects.filter(
            user=self.request.user,
        ).order_by('-date')[:14]
        return ctx


class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'analytics/admin_dashboard.html'

    def test_func(self):
        return self.request.user.is_admin_role

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from django.contrib.auth import get_user_model
        from apps.courses.models import Course, Enrollment
        from apps.careers.models import Job
        from apps.applications.models import JobApplication
        from apps.payments.models import Order
        User = get_user_model()
        ctx['nav_active'] = 'analytics'
        ctx['total_users'] = User.objects.filter(is_active=True).exclude(is_superuser=True).count()
        ctx['total_courses'] = Course.objects.filter(status=Course.PUBLISHED).count()
        ctx['total_jobs'] = Job.objects.filter(status=Job.OPEN).count()
        ctx['total_enrollments'] = Enrollment.objects.count()
        ctx['total_applications'] = JobApplication.objects.count()
        ctx['revenue'] = sum(o.amount for o in Order.objects.filter(status=Order.PAID))
        ctx['recent_users'] = User.objects.exclude(is_superuser=True).order_by('-date_joined')[:10]
        ctx['recent_orders'] = Order.objects.filter(status=Order.PAID).order_by('-paid_at')[:10]
        return ctx
