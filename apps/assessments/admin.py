"""Admin for the assessments app."""
from django.contrib import admin

from .models import (
    Assessment, Question, Choice, AssessmentAttempt, Answer,
)


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'assessment_type', 'course', 'is_published',
                    'duration_minutes', 'passing_score_pct')
    list_filter = ('assessment_type', 'is_published')
    search_fields = ('title', 'description')
    inlines = [QuestionInline]


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('assessment', 'question_type', 'marks', 'order', 'body_preview')
    list_filter = ('question_type',)
    search_fields = ('body',)
    inlines = [ChoiceInline]

    def body_preview(self, obj):
        return obj.body[:80]
    body_preview.short_description = 'Body'


admin.site.register(Choice)
admin.site.register(AssessmentAttempt)
admin.site.register(Answer)
