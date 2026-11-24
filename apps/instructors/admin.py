"""Admin for the instructors app."""
from django.contrib import admin

from .models import InstructorProfile, Payout


@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_verified', 'courses_count',
                    'students_count', 'avg_rating', 'total_earnings')
    list_filter = ('is_verified',)
    search_fields = ('user__email', 'user__first_name', 'title', 'expertise')
    readonly_fields = ('slug', 'courses_count', 'students_count',
                       'avg_rating', 'total_earnings')


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ('instructor', 'amount', 'period_start', 'period_end',
                    'status', 'paid_at')
    list_filter = ('status',)
    search_fields = ('instructor__user__email', 'reference')
    readonly_fields = ('created_at',)
