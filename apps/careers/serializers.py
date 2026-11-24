"""DRF serializers for the careers app."""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Job, JobCategory, JobAlert

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email']


class JobCategorySerializer(serializers.ModelSerializer):
    job_count = serializers.IntegerField(source='jobs.count', read_only=True)

    class Meta:
        model = JobCategory
        fields = ['id', 'name', 'slug', 'description', 'job_count']


class JobBriefSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='employer.company_name', read_only=True)

    class Meta:
        model = Job
        fields = ['id', 'title', 'slug', 'company_name', 'category',
                  'employment_type', 'experience_level',
                  'location_city', 'is_remote', 'is_wfh',
                  'salary_range', 'is_featured', 'posted_at']


class JobSerializer(serializers.ModelSerializer):
    posted_by = UserBriefSerializer(read_only=True)
    salary_range = serializers.CharField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Job
        fields = ['id', 'title', 'slug', 'description', 'requirements',
                  'responsibilities', 'employer', 'posted_by',
                  'category', 'category_name', 'employment_type',
                  'experience_level',
                  'location_city', 'location_state', 'is_remote', 'is_wfh',
                  'salary_min', 'salary_max', 'currency', 'is_salary_disclosed',
                  'skills_required', 'status', 'openings',
                  'application_deadline', 'views_count', 'applications_count',
                  'is_featured', 'is_active', 'salary_range',
                  'posted_at', 'updated_at']
        read_only_fields = ['posted_by', 'slug', 'views_count',
                            'applications_count', 'posted_at', 'updated_at']

    def create(self, validated_data):
        validated_data['posted_by'] = self.context['request'].user
        employer = getattr(self.context['request'].user, 'employer_profile', None)
        if employer:
            validated_data['employer'] = employer
        return super().create(validated_data)


class JobAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobAlert
        fields = ['id', 'user', 'keywords', 'category', 'location_city',
                  'is_remote', 'employment_type', 'min_salary',
                  'frequency', 'is_active', 'last_sent_at', 'created_at']
        read_only_fields = ['user', 'last_sent_at', 'created_at']
