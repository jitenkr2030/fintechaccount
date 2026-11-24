"""DRF serializers for the courses app."""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import (
    Category, Course, Module, Lesson, Enrollment,
    LessonProgress, CourseReview,
)

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'headline']


class CategorySerializer(serializers.ModelSerializer):
    course_count = serializers.IntegerField(source='courses.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'course_count']


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'module', 'title', 'content_type', 'body',
                  'video_url', 'duration_minutes', 'is_preview', 'order']


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'course', 'title', 'description', 'order', 'lessons']


class CourseReviewSerializer(serializers.ModelSerializer):
    student = UserBriefSerializer(read_only=True)

    class Meta:
        model = CourseReview
        fields = ['id', 'course', 'student', 'rating', 'body', 'created_at']
        read_only_fields = ['student', 'created_at']


class CourseSerializer(serializers.ModelSerializer):
    instructor = UserBriefSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)
    reviews = CourseReviewSerializer(many=True, read_only=True)
    is_enrolled = serializers.SerializerMethodField()
    effective_price = serializers.DecimalField(max_digits=10, decimal_places=2,
                                                read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'subtitle', 'description',
                  'category', 'level', 'delivery', 'status',
                  'instructor', 'cover_image', 'promo_video_url',
                  'is_free', 'price', 'discount_price', 'effective_price',
                  'starts_at', 'ends_at', 'duration_hours',
                  'students_count', 'rating', 'reviews_count',
                  'is_featured', 'is_certified', 'is_corporate',
                  'is_enrolled', 'modules', 'reviews',
                  'created_at', 'updated_at']
        read_only_fields = ['instructor', 'slug', 'students_count',
                            'rating', 'reviews_count']

    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.enrollments.filter(student=request.user).exists()

    def create(self, validated_data):
        validated_data['instructor'] = self.context['request'].user
        return super().create(validated_data)


class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    student = UserBriefSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'student', 'status', 'enrolled_at',
                  'completed_at', 'progress_pct']
        read_only_fields = ['student', 'enrolled_at', 'completed_at', 'progress_pct']


class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = ['id', 'enrollment', 'lesson', 'is_completed',
                  'position_seconds', 'completed_at', 'updated_at']
        read_only_fields = ['completed_at', 'updated_at']
