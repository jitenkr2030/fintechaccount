from django.contrib import admin
from .models import UserActivity, Recommendation

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'posts_count', 'comments_count', 'likes_count', 'logins_count', 'course_minutes')
    list_filter = ('date',)
    search_fields = ('user__email',)

@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'source', 'target_type', 'target_text', 'score', 'is_clicked', 'is_dismissed', 'created_at')
    list_filter = ('source', 'is_clicked', 'is_dismissed')
    search_fields = ('user__email', 'target_text')
    readonly_fields = ('created_at',)
