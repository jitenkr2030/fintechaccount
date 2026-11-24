"""DRF serializers for the applications app."""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import JobApplication

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    headline = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'headline']


class JobApplicationSerializer(serializers.ModelSerializer):
    applicant = UserBriefSerializer(read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_slug = serializers.CharField(source='job.slug', read_only=True)
    company_name = serializers.CharField(source='job.employer.company_name',
                                          read_only=True)

    class Meta:
        model = JobApplication
        fields = ['id', 'job', 'job_title', 'job_slug', 'company_name',
                  'applicant', 'cover_letter', 'resume', 'expected_salary',
                  'notice_period_days', 'status', 'employer_notes', 'rating',
                  'consent_verify_credentials', 'applied_at', 'updated_at']
        read_only_fields = ['applicant', 'status', 'employer_notes', 'rating',
                            'applied_at', 'updated_at']

    def create(self, validated_data):
        validated_data['applicant'] = self.context['request'].user
        return super().create(validated_data)
