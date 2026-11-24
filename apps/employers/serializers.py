"""DRF serializers for the employers app."""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import EmployerProfile, Interview

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email']


class EmployerProfileSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(read_only=True)
    job_count = serializers.SerializerMethodField()

    class Meta:
        model = EmployerProfile
        fields = ['id', 'user', 'slug', 'company_name', 'tagline', 'about',
                  'logo', 'website', 'linkedin', 'industry', 'company_size',
                  'headquarters_city', 'headquarters_state', 'country',
                  'contact_name', 'contact_email', 'contact_phone',
                  'is_verified', 'jobs_count', 'hires_count',
                  'job_count', 'created_at']
        read_only_fields = ['user', 'slug', 'is_verified', 'jobs_count', 'hires_count']

    def get_job_count(self, obj):
        return obj.jobs.count()

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = ['id', 'application', 'interviewer', 'scheduled_at',
                  'duration_minutes', 'location', 'notes', 'status',
                  'feedback', 'created_at']
        read_only_fields = ['interviewer', 'created_at']
