"""Admin for the employers app."""
from django.contrib import admin

from .models import EmployerProfile, Interview


@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'industry', 'company_size',
                    'is_verified', 'jobs_count', 'hires_count', 'created_at')
    list_filter = ('is_verified', 'industry', 'company_size')
    search_fields = ('company_name', 'user__email', 'headquarters_city')
    readonly_fields = ('slug', 'jobs_count', 'hires_count',
                       'created_at', 'updated_at')


admin.site.register(Interview)
