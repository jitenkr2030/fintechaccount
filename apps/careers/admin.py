"""Admin for the careers app."""
from django.contrib import admin

from .models import JobCategory, Job, JobAlert


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'category', 'employment_type',
                    'experience_level', 'status', 'is_featured',
                    'applications_count', 'posted_at')
    list_filter = ('status', 'employment_type', 'experience_level',
                    'is_featured', 'is_remote', 'category')
    search_fields = ('title', 'description', 'location_city',
                     'posted_by__email')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views_count', 'applications_count', 'posted_at', 'updated_at')


@admin.register(JobAlert)
class JobAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'keywords', 'category', 'frequency',
                    'is_active', 'last_sent_at')
    list_filter = ('frequency', 'is_active')
    search_fields = ('user__email', 'keywords')
