"""Admin for the courses app."""
from django.contrib import admin

from .models import (
    Category, Course, Module, Lesson, Enrollment,
    LessonProgress, CourseReview,
)


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    show_change_link = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'description')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'level', 'delivery', 'status',
                    'is_free', 'price', 'is_featured', 'students_count',
                    'rating', 'is_corporate')
    list_filter = ('status', 'level', 'delivery', 'is_free',
                   'is_featured', 'is_corporate', 'category')
    search_fields = ('title', 'subtitle', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('students_count', 'rating', 'reviews_count')
    inlines = [ModuleInline]


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('course', 'title', 'order')
    list_filter = ('course__category',)
    search_fields = ('title',)
    inlines = [LessonInline]


admin.site.register(Lesson)
admin.site.register(Enrollment)
admin.site.register(LessonProgress)
admin.site.register(CourseReview)
