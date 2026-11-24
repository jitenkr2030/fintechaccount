"""Home and dashboard views."""
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.db.models import Count, Sum


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['brand'] = settings.BRAND
        ctx['nav_active'] = 'home'

        # Rich home page data — featured courses, jobs, communities, events
        from apps.courses.models import Course, Category, Enrollment
        from apps.careers.models import Job, JobCategory
        from apps.communities.models import Community
        from apps.events.models import Event
        from apps.accounts.models import User
        from django.utils import timezone

        ctx['featured_courses'] = (
            Course.objects.filter(status=Course.PUBLISHED, is_featured=True)
            .select_related('instructor', 'category')[:6]
        )
        if not ctx['featured_courses']:
            ctx['featured_courses'] = (
                Course.objects.filter(status=Course.PUBLISHED)
                .select_related('instructor', 'category')[:6]
            )
        ctx['course_categories'] = Category.objects.all()[:8]

        ctx['featured_jobs'] = (
            Job.objects.filter(status=Job.OPEN, is_featured=True)
            .select_related('employer', 'category')[:6]
        )
        if not ctx['featured_jobs']:
            ctx['featured_jobs'] = (
                Job.objects.filter(status=Job.OPEN)
                .select_related('employer', 'category')[:6]
            )

        ctx['official_communities'] = (
            Community.objects.filter(is_official=True).order_by('-members_count')[:6]
        )
        if not ctx['official_communities']:
            ctx['official_communities'] = Community.objects.order_by('-members_count')[:6]

        ctx['upcoming_events'] = (
            Event.objects.filter(status=Event.PUBLISHED, starts_at__gt=timezone.now())
            .order_by('starts_at')[:3]
        )

        # Stats for hero strip
        ctx['stats'] = {
            'members': User.objects.filter(is_active=True).exclude(is_superuser=True).count(),
            'courses': Course.objects.filter(status=Course.PUBLISHED).count(),
            'jobs': Job.objects.filter(status=Job.OPEN).count(),
            'communities': Community.objects.count(),
        }

        # Pillars data
        ctx['pillars'] = [
            {
                'name': 'Network',
                'tagline': 'Connect with professionals',
                'desc': 'Build relationships with accountants, finance experts, students and employers across India.',
                'url': '/network/',
                'icon': 'people-fill',
                'color': 'brand',
                'items': ['Professional profiles', 'News feed & articles', 'Communities & groups', 'Direct messaging', 'Events & webinars', 'Mentorship'],
            },
            {
                'name': 'Courses',
                'tagline': 'Build finance & fintech skills',
                'desc': 'Learn accounting, taxation, finance, FinTech and technology from industry experts.',
                'url': '/courses/',
                'icon': 'mortarboard-fill',
                'color': 'gold',
                'items': ['Free & paid courses', 'Live & recorded classes', 'Instructor profiles', 'Student dashboard', 'Assignments & exams', 'Completion certificates'],
            },
            {
                'name': 'Careers',
                'tagline': 'Find jobs and opportunities',
                'desc': 'Discover jobs, internships and freelance projects in finance and FinTech.',
                'url': '/careers/',
                'icon': 'briefcase-fill',
                'color': 'teal',
                'items': ['Job search', 'Internships', 'Freelance projects', 'Remote & WFH', 'Application tracking', 'Job alerts'],
            },
        ]

        # Career categories for the "explore" section
        ctx['job_categories'] = JobCategory.objects.annotate(
            job_count=Count('jobs'),
        ).filter(job_count__gt=0).order_by('-job_count')[:8]
        return ctx


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['brand'] = settings.BRAND
        ctx['nav_active'] = 'dashboard'
        ctx['pillars'] = [
            {
                'name': 'Network',
                'tagline': 'Connect with professionals',
                'url': '/network/',
                'icon': 'people',
                'items': ['News Feed', 'Communities', 'Messages', 'Events'],
            },
            {
                'name': 'Courses',
                'tagline': 'Build finance & fintech skills',
                'url': '/courses/',
                'icon': 'school',
                'items': ['Course Catalog', 'My Learning', 'Certificates', 'Instructors'],
            },
            {
                'name': 'Careers',
                'tagline': 'Find jobs and opportunities',
                'url': '/careers/',
                'icon': 'work',
                'items': ['Job Search', 'My Applications', 'Employer Profiles', 'Resume'],
            },
        ]
        return ctx
