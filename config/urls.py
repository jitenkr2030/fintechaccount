"""FinTech Accountant - root URL configuration.

Routing convention:
    /                        -> public landing page + dashboard
    /accounts/               -> Phase 1  - auth, registration, roles
    /profiles/               -> Phase 1  - professional profiles & directory
    /network/                -> Phase 2  - posts, feed, connections
    /communities/            -> Phase 2  - groups & communities
    /messaging/              -> Phase 2  - direct messaging
    /events/                 -> Phase 2  - webinars & events
    /courses/                -> Phase 3  - learning catalog & enrollment
    /instructors/            -> Phase 3  - instructor profiles
    /assessments/            -> Phase 3  - quizzes & exams
    /certificates/           -> Phase 3  - course completion certificates
    /careers/                -> Phase 4  - job listings & search
    /employers/              -> Phase 4  - employer/company profiles
    /applications/           -> Phase 4  - job applications & tracking
    /payments/               -> Phase 3+ - Razorpay payments
    /notifications/          -> shared   - in-app notifications
    /moderation/             -> shared   - content moderation queue
    /analytics/              -> Phase 5  - dashboards & AI recommendations
    /api/v1/                 -> DRF REST API for all apps above
    /api/auth/               -> JWT token obtain/refresh
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from config.views import HomeView, DashboardView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from config.api_urls import api_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),

    # Public landing
    path('', HomeView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),

    # Pillar A - Network
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('profiles/', include('apps.profiles.urls', namespace='profiles')),
    path('network/', include('apps.networking.urls', namespace='networking')),
    path('communities/', include('apps.communities.urls', namespace='communities')),
    path('messaging/', include('apps.messaging.urls', namespace='messaging')),
    path('events/', include('apps.events.urls', namespace='events')),

    # Pillar B - Learning
    path('courses/', include('apps.courses.urls', namespace='courses')),
    path('instructors/', include('apps.instructors.urls', namespace='instructors')),
    path('assessments/', include('apps.assessments.urls', namespace='assessments')),
    path('certificates/', include('apps.certificates.urls', namespace='certificates')),

    # Pillar C - Careers
    path('careers/', include('apps.careers.urls', namespace='careers')),
    path('employers/', include('apps.employers.urls', namespace='employers')),
    path('applications/', include('apps.applications.urls', namespace='applications')),

    # Shared services
    path('payments/', include('apps.payments.urls', namespace='payments')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),
    path('moderation/', include('apps.moderation.urls', namespace='moderation')),
    path('analytics/', include('apps.analytics.urls', namespace='analytics')),

    # REST API
    path('api/v1/', include(api_urlpatterns)),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
