"""DRF serializers for the certificates app."""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Certificate, CertificateTemplate

User = get_user_model()


class UserBriefSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email']


class CertificateTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateTemplate
        fields = ['id', 'name', 'description', 'template_html', 'is_default']


class CertificateSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    disclaimer = serializers.CharField(read_only=True)
    is_platform_issued = serializers.BooleanField(read_only=True)

    class Meta:
        model = Certificate
        fields = ['id', 'certificate_id', 'verification_code', 'user',
                  'course', 'course_title', 'enrollment',
                  'issued_at', 'status', 'final_score_pct', 'grade',
                  'is_platform_issued', 'disclaimer', 'pdf', 'created_at']
        read_only_fields = ['certificate_id', 'verification_code', 'issued_at',
                            'user', 'status', 'is_platform_issued', 'disclaimer']
