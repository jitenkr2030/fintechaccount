"""Admin for the profiles app."""
from django.contrib import admin

from .models import (
    Skill, Profile, Education, Experience, Certification,
    ProfileSkill, PortfolioItem,
)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)


class EducationInline(admin.TabularInline):
    model = Education
    extra = 1


class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 1


class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 1


class ProfileSkillInline(admin.TabularInline):
    model = ProfileSkill
    extra = 1


class PortfolioInline(admin.TabularInline):
    model = PortfolioItem
    extra = 1


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_title', 'current_company', 'industry',
                    'is_verified_professional', 'is_open_to_work', 'completion_pct')
    list_filter = ('is_verified_professional', 'is_open_to_work', 'is_open_to_mentor', 'industry')
    search_fields = ('user__email', 'user__first_name', 'user__last_name',
                     'current_title', 'current_company')
    inlines = [ExperienceInline, EducationInline, CertificationInline,
               ProfileSkillInline, PortfolioInline]
    readonly_fields = ('created_at', 'updated_at', 'followers_count',
                       'following_count', 'posts_count', 'completion_pct')


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('profile', 'name', 'issuing_body', 'is_statutory', 'is_verified')
    list_filter = ('is_statutory', 'is_verified', 'issuing_body')
    search_fields = ('name', 'issuing_body', 'credential_id')


admin.site.register(Education)
admin.site.register(Experience)
admin.site.register(ProfileSkill)
admin.site.register(PortfolioItem)
