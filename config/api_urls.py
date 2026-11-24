"""Consolidated DRF API routing for all apps under /api/v1/."""
from django.urls import path, include

api_urlpatterns = [
    # Auth
    path('accounts/', include('apps.accounts.api_urls')),

    # Pillar A - Network
    path('profiles/', include('apps.profiles.api_urls')),
    path('network/', include('apps.networking.api_urls')),
    path('communities/', include('apps.communities.api_urls')),
    path('messaging/', include('apps.messaging.api_urls')),
    path('events/', include('apps.events.api_urls')),

    # Pillar B - Learning
    path('courses/', include('apps.courses.api_urls')),
    path('instructors/', include('apps.instructors.api_urls')),
    path('assessments/', include('apps.assessments.api_urls')),
    path('certificates/', include('apps.certificates.api_urls')),

    # Pillar C - Careers
    path('careers/', include('apps.careers.api_urls')),
    path('employers/', include('apps.employers.api_urls')),
    path('applications/', include('apps.applications.api_urls')),

    # Shared services
    path('payments/', include('apps.payments.api_urls')),
    path('notifications/', include('apps.notifications.api_urls')),
    path('moderation/', include('apps.moderation.api_urls')),
    path('analytics/', include('apps.analytics.api_urls')),
]
