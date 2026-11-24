"""Admin for the communities app."""
from django.contrib import admin

from .models import Community, CommunityMembership, CommunityTopic, CommunityReply


class MembershipInline(admin.TabularInline):
    model = CommunityMembership
    extra = 1


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'visibility', 'is_official',
                    'members_count', 'posts_count')
    list_filter = ('visibility', 'is_official', 'category')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [MembershipInline]
    readonly_fields = ('members_count', 'posts_count')


admin.site.register(CommunityMembership)
admin.site.register(CommunityTopic)
admin.site.register(CommunityReply)
