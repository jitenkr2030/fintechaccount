"""DRF serializers for the instructors app."""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import InstructorProfile, Payout

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'headline']


class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = ['id', 'instructor', 'amount', 'period_start', 'period_end',
                  'status', 'paid_at', 'reference', 'notes', 'created_at']
        read_only_fields = ['paid_at', 'created_at']


class InstructorProfileSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(read_only=True)
    course_count = serializers.SerializerMethodField()

    class Meta:
        model = InstructorProfile
        fields = ['id', 'user', 'slug', 'title', 'bio', 'expertise',
                  'years_teaching', 'certifications', 'website', 'linkedin',
                  'youtube', 'courses_count', 'students_count', 'avg_rating',
                  'total_earnings', 'is_verified', 'commission_pct',
                  'course_count', 'created_at']
        read_only_fields = ['user', 'slug', 'courses_count', 'students_count',
                            'avg_rating', 'total_earnings', 'is_verified']

    def get_course_count(self, obj):
        return obj.user.courses_taught.count()
