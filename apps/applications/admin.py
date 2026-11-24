"""Admin for the applications app."""
from django.contrib import admin

from .models import JobApplication


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'job', 'status', 'rating',
                    'consent_verify_credentials', 'applied_at')
    list_filter = ('status', 'consent_verify_credentials', 'rating')
    search_fields = ('applicant__email', 'job__title', 'cover_letter')
    readonly_fields = ('applied_at', 'updated_at')
    filter_horizontal = ()
